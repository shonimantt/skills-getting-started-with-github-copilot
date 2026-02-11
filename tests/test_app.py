"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state after each test"""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and inter-school tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Join our soccer team for friendly matches and skill development",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions and challenges",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debate tournaments and develop public speaking skills",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_chess_club(self, client):
        """Test that GET /activities returns Chess Club"""
        response = client.get("/activities")
        assert "Chess Club" in response.json()
    
    def test_get_activities_chess_club_has_required_fields(self, client):
        """Test that Chess Club has all required fields"""
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_get_activities_includes_all_activities(self, client):
        """Test that GET /activities returns all 9 activities"""
        response = client.get("/activities")
        assert len(response.json()) == 9


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_returns_200(self, client, reset_activities):
        """Test that signing up a new student returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_new_student_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    def test_signup_new_student_adds_to_participants(self, client, reset_activities):
        """Test that signup adds student to participants list"""
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signing up for a nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_registered_returns_400(self, client, reset_activities):
        """Test that signing up an already registered student returns 400"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity"""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": student1}
        )
        response2 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": student2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert student1 in participants
        assert student2 in participants


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_returns_200(self, client, reset_activities):
        """Test that unregistering an existing student returns 200"""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_unregister_existing_student_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
    
    def test_unregister_removes_from_participants(self, client, reset_activities):
        """Test that unregister removes student from participants list"""
        client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregistering from a nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_registered_returns_400(self, client, reset_activities):
        """Test that unregistering a non-registered student returns 400"""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
