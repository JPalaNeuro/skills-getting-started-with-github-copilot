import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module

# Ensure tests do not depend on previous state
@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original

client = TestClient(app_module.app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_reflects_in_get():
    email = "unit@test.com"
    r = client.post("/activities/Chess%20Club/signup?email=" + email)
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    r2 = client.get("/activities")
    assert email in r2.json()["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "dup@test.com"
    r1 = client.post("/activities/Chess%20Club/signup?email=" + email)
    assert r1.status_code == 200

    r2 = client.post("/activities/Chess%20Club/signup?email=" + email)
    assert r2.status_code == 400
    assert "Student already signed up" in r2.json()["detail"]


def test_unregister_removes_participant():
    email = "remove@test.com"
    client.post("/activities/Chess%20Club/signup?email=" + email)

    r = client.post("/activities/Chess%20Club/unregister?email=" + email)
    assert r.status_code == 200
    assert "Unregistered" in r.json()["message"]

    r2 = client.get("/activities")
    assert email not in r2.json()["Chess Club"]["participants"]


def test_unregister_nonexistent_returns_404():
    r = client.post("/activities/Chess%20Club/unregister?email=notfound@test.com")
    assert r.status_code == 404
    assert "Student not found" in r.json()["detail"]
