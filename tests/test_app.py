import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that the root endpoint returns index.html"""
    response = client.get("/")
    assert response.status_code == 200  # OK
    # The redirect is handled by FastAPI's StaticFiles, so we get the content directly


def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Test structure of an activity
    first_activity = list(activities.values())[0]
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Test successful signup
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify student was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First, sign up a student
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    email = "unregistertest@mergington.edu"
    
    # Sign up the student
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Test successful unregistration
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Test unregistering when not registered
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()


def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.post("/activities/nonexistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()