import sys
from pathlib import Path

# Ensure the src directory is on sys.path so we can import app
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect activities dict with at least one known key
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Make sure this email isn't already signed up (if it is, try to remove it first)
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Check participant appears
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Check participant removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email not in participants
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure src is on path so we can import app
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Some known activity present
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    test_email = "test.student@example.com"
    activity = "Programming Class"

    # Ensure email is not already a participant (if it is, remove it)
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    if test_email in activities.get(activity, {}).get("participants", []):
        # attempt to remove so test starts from clean state
        del_resp = client.delete(f"/activities/{activity}/unregister?email={test_email}")
        # ignore result; best-effort cleanup

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert signup_resp.status_code == 200
    signup_json = signup_resp.json()
    assert "Signed up" in signup_json.get("message", "")

    # Verify participant appears in activities
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    activities2 = resp2.json()
    assert test_email in activities2.get(activity, {}).get("participants", [])

    # Unregister
    unreg_resp = client.delete(f"/activities/{activity}/unregister?email={test_email}")
    assert unreg_resp.status_code == 200
    unreg_json = unreg_resp.json()
    assert "Unregistered" in unreg_json.get("message", "")

    # Verify removed
    resp3 = client.get("/activities")
    activities3 = resp3.json()
    assert test_email not in activities3.get(activity, {}).get("participants", [])


def test_unregister_nonexistent():
    test_email = "nonexistent@example.com"
    activity = "Drama Club"

    # Ensure the email is not present
    resp = client.get("/activities")
    activities = resp.json()
    if test_email in activities.get(activity, {}).get("participants", []):
        client.delete(f"/activities/{activity}/unregister?email={test_email}")

    del_resp = client.delete(f"/activities/{activity}/unregister?email={test_email}")
    # Should be 400 because student not signed up
    assert del_resp.status_code == 400
    data = del_resp.json()
    assert "Student is not signed up" in data.get("detail", "")
