from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange: no special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Signed up {email} for {activity_name}"

    # Cleanup
    client.delete(f"/activities/{activity_name}/participants/{email}")


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate_student@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student already signed up for this activity"

    # Cleanup
    client.delete(f"/activities/{activity_name}/participants/{email}")


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Programming Class"
    email = "remove_student@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Removed {email} from {activity_name}"


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "missing_student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Participant not found"
