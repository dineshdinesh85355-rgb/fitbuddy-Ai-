from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)
from .gemini_generator import (
    generate_workout_gemini
)
from .models import User
from .schemas import (
    FeedbackRequest,
    UserInput
)
from .updated_plan import (
    update_workout_plan
)


router = APIRouter()


TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent / "templates"
)


templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


def render_error(
    request: Request,
    message: str,
    status_code: int = 400
):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "message": message
        },
        status_code=status_code
    )


# -------------------------------------------------
# HOME
# -------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# -------------------------------------------------
# GENERATE WORKOUT
# -------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

    except Exception as exc:

        return render_error(
            request,
            str(exc),
            422
        )

    # Check duplicate user ID

    existing_user = db.scalar(
        select(User).where(
            User.user_id == data.user_id
        )
    )

    if existing_user:

        return render_error(
            request,
            "This User ID already exists. "
            "Use another User ID or submit feedback "
            "for the existing plan.",
            409
        )

    # Generate workout

    workout_plan = generate_workout_gemini(
        name=data.username,
        age=data.age,
        weight=data.weight,
        goal=data.goal,
        intensity=data.intensity
    )

    # Generate nutrition tip

    nutrition_tip = (
        generate_nutrition_tip_with_flash(
            data.goal
        )
    )

    # Save user

    user = User(

        user_id=data.user_id,

        name=data.username,

        age=data.age,

        weight=data.weight,

        goal=data.goal,

        intensity=data.intensity,

        original_plan=workout_plan,

        nutrition_tip=nutrition_tip

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "user": user,

            "plan": user.original_plan,

            "tip": user.nutrition_tip,

            "updated": False,

            "message":
                "Your personalized plan has been generated."

        }
    )


# -------------------------------------------------
# SUBMIT FEEDBACK
# -------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)

):

    try:

        data = FeedbackRequest(

            user_id=user_id,

            feedback=feedback

        )

    except Exception as exc:

        return render_error(
            request,
            str(exc),
            422
        )

    user = db.scalar(

        select(User).where(
            User.user_id == data.user_id
        )

    )

    if not user:

        return render_error(
            request,
            "User ID not found.",
            404
        )

    # Generate revised plan

    revised_plan = update_workout_plan(

        original_plan=user.original_plan,

        feedback=data.feedback

    )

    # Save update

    user.updated_plan = revised_plan

    user.feedback = data.feedback

    db.commit()

    db.refresh(user)

    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "user": user,

            "plan": user.updated_plan,

            "tip": user.nutrition_tip,

            "updated": True,

            "message":
                "Your workout plan has been updated."

        }

    )


# -------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------

def admin_authorized(
    request: Request
) -> bool:

    settings = get_settings()

    return (
        request.cookies.get("fitbuddy_admin")
        == settings.admin_password
    )


# -------------------------------------------------
# ADMIN DASHBOARD
# -------------------------------------------------

@router.get(
    "/admin",
    response_class=HTMLResponse
)
def admin_page(

    request: Request,

    password: str | None = None,

    db: Session = Depends(get_db)

):

    settings = get_settings()

    # Login attempt

    if (
        password is not None
        and password == settings.admin_password
    ):

        response = RedirectResponse(
            "/admin",
            status_code=status.HTTP_303_SEE_OTHER
        )

        response.set_cookie(

            "fitbuddy_admin",

            settings.admin_password,

            httponly=True,

            samesite="lax"

        )

        return response

    # Not authenticated

    if not admin_authorized(request):

        return templates.TemplateResponse(

            request=request,

            name="all_users.html",

            context={
                "users": [],
                "requires_login": True
            }

        )

    # Get all users

    users = list(

        db.scalars(

            select(User)
            .order_by(
                User.created_at.desc()
            )

        ).all()

    )

    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={
            "users": users,
            "requires_login": False
        }

    )


# -------------------------------------------------
# API: ALL USERS
# -------------------------------------------------

@router.get("/api/users")
def api_users(

    request: Request,

    db: Session = Depends(get_db)

):

    if not admin_authorized(request):

        raise HTTPException(
            status_code=401,
            detail="Admin authentication required."
        )

    users = list(

        db.scalars(

            select(User)
            .order_by(
                User.created_at.desc()
            )

        ).all()

    )

    return [

        {
            "user_id": user.user_id,

            "name": user.name,

            "age": user.age,

            "weight": user.weight,

            "goal": user.goal,

            "intensity": user.intensity,

            "original_plan":
                user.original_plan,

            "updated_plan":
                user.updated_plan,

            "feedback":
                user.feedback,

            "created_at":
                user.created_at.isoformat()
        }

        for user in users

    ]


# -------------------------------------------------
# API: SINGLE USER
# -------------------------------------------------

@router.get(
    "/api/users/{user_id}"
)
def api_user(

    user_id: str,

    request: Request,

    db: Session = Depends(get_db)

):

    if not admin_authorized(request):

        raise HTTPException(
            status_code=401,
            detail="Admin authentication required."
        )

    user = db.scalar(

        select(User).where(
            User.user_id == user_id
        )

    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {

        "user_id":
            user.user_id,

        "name":
            user.name,

        "age":
            user.age,

        "weight":
            user.weight,

        "goal":
            user.goal,

        "intensity":
            user.intensity,

        "original_plan":
            user.original_plan,

        "updated_plan":
            user.updated_plan,

        "feedback":
            user.feedback

    }