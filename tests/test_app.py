import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Create a test client
client = TestClient(app)

# Store original activities for reset
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update(original_activities)

def test_root_redirect():
    """Test GET / redirects to static HTML"""
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test GET /activities returns all activities"""
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Number of activities
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1

def test_signup_already_signed_up():
    """Test signup when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    """Test successful unregister from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    initial_participants = activities[activity_name]["participants"].copy()
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) - 1

def test_unregister_not_signed_up():
    """Test unregister when student is not signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity():
    """Test unregister from non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]