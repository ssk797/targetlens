from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_is_mock_mode() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["mode"] == "mock"


def test_create_and_fetch_session() -> None:
    created = client.post("/api/v1/sessions", json={"question": "EGFR 的证据成熟度如何？"})
    assert created.status_code == 201
    session_id = created.json()["id"]
    fetched = client.get(f"/api/v1/sessions/{session_id}")
    assert fetched.status_code == 200
    assert fetched.json()["question"].startswith("EGFR")


def test_research_returns_accepted_job() -> None:
    response = client.post("/api/v1/sessions/session-ror1/research")
    assert response.status_code == 202
    assert response.json()["status"] == "QUEUED"
    assert response.json()["events_url"].endswith("/events")


def test_events_stream_contains_completion() -> None:
    response = client.get("/api/v1/sessions/session-ror1/events")
    assert response.status_code == 200
    assert "research.completed" in response.text
