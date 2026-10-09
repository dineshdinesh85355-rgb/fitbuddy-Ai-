import os

os.environ["DATABASE_URL"] = (
    "sqlite:///./test_fitbuddy.db"
)

os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_plan():

    response = client.post(

        "/generate-workout",

        data={

            "username":
                "Test User",

            "user_id":
                "TEST001",

            "age":
                "18",

            "weight":
                "60",

            "goal":
                "General wellness",

            "intensity":
                "medium"

        }

    )

    assert response.status_code == 200

    assert "7-Day" in response.text


def test_feedback():

    response = client.post(

        "/submit-feedback",

        data={

            "user_id":
                "TEST001",

            "feedback":
                "Please include another recovery day."

        }

    )

    assert response.status_code == 200

    assert "updated" in (
        response.text.lower()
    )