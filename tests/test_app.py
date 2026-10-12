import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

BASELINE_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(BASELINE_ACTIVITIES))


def test_get_activities_returns_activity_list():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_success():
    reset_activities()
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_rejected():
    reset_activities()
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_participant_success():
    reset_activities()
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_not_found():
    reset_activities()
    email = "missing.student@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()


def test_unknown_activity_returns_404():
    reset_activities()

    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "test.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
