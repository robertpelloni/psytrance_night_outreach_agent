import os
import pytest
from unittest.mock import patch
from src.db_manager import DatabaseManager
from src.dashboard.app import app

TEST_DB_PATH = "database/test_feedback_unit.db"

@pytest.fixture
def test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = DatabaseManager(db_path=TEST_DB_PATH)
    yield db
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_database_feedback_persistence(test_db):
    fid = test_db.record_operator_feedback("Vibe Calibration", "Increase minimum vibe to 7.0 in Ann Arbor.", author="Curator1")
    assert fid is not None
    feedbacks = test_db.get_operator_feedback()
    assert len(feedbacks) == 1
    assert feedbacks[0]["category"] == "Vibe Calibration"
    assert feedbacks[0]["author"] == "Curator1"
    assert feedbacks[0]["status"] == "PENDING"
    assert "Ann Arbor" in feedbacks[0]["message"]

    # Test status update
    updated = test_db.update_operator_feedback_status(fid, "IN_REVIEW")
    assert updated is True
    feedbacks_in_review = test_db.get_operator_feedback(status="IN_REVIEW")
    assert len(feedbacks_in_review) == 1
    assert feedbacks_in_review[0]["status"] == "IN_REVIEW"

    # Test resolve
    test_db.update_operator_feedback_status(fid, "RESOLVED")
    assert len(test_db.get_operator_feedback(status="RESOLVED")) == 1
    assert len(test_db.get_operator_feedback(status="PENDING")) == 0

def test_submit_feedback_endpoint_json(test_db):
    app.config["TESTING"] = True
    with patch("src.dashboard.app.db", test_db):
        client = app.test_client()
        res = client.post("/submit_feedback", json={
            "category": "Circuit Routing",
            "message": "Add Grand Rapids stop between Detroit and Chicago.",
            "author": "TourManager"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "feedback_id" in data

        items = test_db.get_operator_feedback()
        assert len(items) == 1
        assert items[0]["category"] == "Circuit Routing"

def test_submit_feedback_empty_validation(test_db):
    app.config["TESTING"] = True
    with patch("src.dashboard.app.db", test_db):
        client = app.test_client()
        res = client.post("/submit_feedback", json={"category": "General", "message": "   "})
        assert res.status_code == 400
        data = res.get_json()
        assert data["status"] == "error"

def test_get_feedback_api(test_db):
    app.config["TESTING"] = True
    test_db.record_operator_feedback("UI / UX", "Navbar looks great in dark mode.", author="Auditor")
    with patch("src.dashboard.app.db", test_db):
        client = app.test_client()
        res = client.get("/api/feedback?limit=10")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["count"] == 1
        assert data["feedback"][0]["author"] == "Auditor"

def test_update_feedback_status_endpoint(test_db):
    app.config["TESTING"] = True
    fid = test_db.record_operator_feedback("Bug Report", "Test bug report", author="Tester")
    with patch("src.dashboard.app.db", test_db):
        client = app.test_client()
        # Test updating to IN_REVIEW
        res = client.post(f"/update_feedback_status/{fid}", json={"status": "IN_REVIEW"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["new_status"] == "IN_REVIEW"

        # Check DB
        items = test_db.get_operator_feedback()
        assert items[0]["status"] == "IN_REVIEW"

        # Test updating to RESOLVED
        res2 = client.post(f"/update_feedback_status/{fid}", json={"status": "RESOLVED"})
        assert res2.status_code == 200
        assert res2.get_json()["new_status"] == "RESOLVED"

        # Check filter via API
        res3 = client.get("/api/feedback?status=RESOLVED")
        assert res3.get_json()["count"] == 1
        res4 = client.get("/api/feedback?status=PENDING")
        assert res4.get_json()["count"] == 0
