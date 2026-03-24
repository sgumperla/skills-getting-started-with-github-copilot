"""
Tests for FastAPI application endpoints.
"""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint."""
    
    def test_get_activities_returns_dict(self, client_with_clean_activities):
        """Verify GET /activities returns a dictionary."""
        response = client_with_clean_activities.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client_with_clean_activities):
        """Verify GET /activities contains expected activity names."""
        response = client_with_clean_activities.get("/activities")
        data = response.json()
        
        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Band",
            "Debate Team",
            "Science Club"
        }
        
        assert expected_activities.issubset(set(data.keys()))
    
    def test_get_activities_has_required_fields(self, client_with_clean_activities):
        """Verify each activity has required fields."""
        response = client_with_clean_activities.get("/activities")
        data = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_info in data.items():
            assert required_fields.issubset(set(activity_info.keys())), \
                f"Activity '{activity_name}' missing required fields"


class TestRootRedirect:
    """Test cases for GET / endpoint."""
    
    def test_root_redirect_to_static_index(self, client_with_clean_activities):
        """Verify GET / redirects to /static/index.html."""
        response = client_with_clean_activities.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client_with_clean_activities):
        """Verify successful signup adds email to activity participants."""
        response = client_with_clean_activities.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client_with_clean_activities.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_email_rejected(self, client_with_clean_activities):
        """Verify duplicate email signup returns 400 error."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client_with_clean_activities.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client_with_clean_activities.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "Student already signed up for this activity" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_rejected(self, client_with_clean_activities):
        """Verify signup for non-existent activity returns 404 error."""
        response = client_with_clean_activities.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_increments_participant_count(self, client_with_clean_activities):
        """Verify participant count increases after signup."""
        # Get initial participant count
        activities_before = client_with_clean_activities.get("/activities").json()
        initial_count = len(activities_before["Programming Class"]["participants"])
        
        # Signup new student
        client_with_clean_activities.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Verify participant count increased
        activities_after = client_with_clean_activities.get("/activities").json()
        final_count = len(activities_after["Programming Class"]["participants"])
        assert final_count == initial_count + 1
    
    def test_signup_multiple_different_students(self, client_with_clean_activities):
        """Verify multiple different students can sign up for the same activity."""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client_with_clean_activities.post(
                "/activities/Music Band/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students are participants
        activities = client_with_clean_activities.get("/activities").json()
        participants = activities["Music Band"]["participants"]
        
        for email in emails:
            assert email in participants
        
        assert len(participants) == len(emails)
    
    def test_signup_returns_correct_message(self, client_with_clean_activities):
        """Verify signup response contains correct message format."""
        email = "test@mergington.edu"
        activity = "Tennis Club"
        
        response = client_with_clean_activities.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
