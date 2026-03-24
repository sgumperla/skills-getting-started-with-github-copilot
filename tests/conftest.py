"""
Pytest configuration and fixtures for testing the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making HTTP requests to the app.
    """
    return TestClient(app)


@pytest.fixture
def clean_activities():
    """
    Fixture that saves the original activities state before each test
    and restores it after the test completes, ensuring test isolation.
    """
    # Save the original state
    original_activities = {k: {"participants": v["participants"].copy(), **{kk: vv for kk, vv in v.items() if kk != "participants"}} for k, v in activities.items()}
    
    # Clear participants for each test
    for activity_key in activities:
        activities[activity_key]["participants"] = []
    
    yield activities
    
    # Restore original state after the test
    activities.clear()
    activities.update({k: {"participants": v["participants"].copy(), **{kk: vv for kk, vv in v.items() if kk != "participants"}} for k, v in original_activities.items()})


@pytest.fixture
def client_with_clean_activities(client, clean_activities):
    """
    Combined fixture providing both TestClient and clean activities state.
    """
    return client
