from fastapi.testclient import TestClient

from app.main import app
from app.services.research.connectors import ConnectorResult, ResearchBundle


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


def test_ai_status_never_exposes_the_api_key() -> None:
    response = client.get("/api/v1/ai/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "deepseek"
    assert "api_key" not in payload


def test_research_preview_normalizes_connector_results(monkeypatch) -> None:
    async def fake_search(self, target: str, disease: str | None = None, modality: str | None = None) -> ResearchBundle:
        return ResearchBundle(
            target=target,
            disease=disease,
            modality=modality,
            connectors=[ConnectorResult(connector="pubmed", status="READY")],
            items=[],
            graph_nodes=[],
            graph_relations=[],
        )

    monkeypatch.setattr("app.main.ResearchAggregator.search", fake_search)
    response = client.post("/api/v1/research/preview", json={"target": "ROR1", "disease": "TNBC", "modality": "ADC"})

    assert response.status_code == 200
    assert response.json()["target"] == "ROR1"
    assert response.json()["connectors"][0]["connector"] == "pubmed"


def test_research_card_and_message_history_keep_target_context() -> None:
    created = client.post("/api/v1/sessions", json={"question": "JAK2 在骨髓增殖性肿瘤中是否适合开发小分子？"})
    assert created.status_code == 201
    session_id = created.json()["id"]
    research = client.post(f"/api/v1/sessions/{session_id}/research", json={"question": created.json()["question"]})
    assert research.status_code == 202
    card = client.get(f"/api/v1/sessions/{session_id}/target-card").json()
    assert card["target"]["symbol"] == "JAK2"
    assert card["scope"]["modality"] == "小分子"
    assert card["metadata"]["isMock"] is True

    answer = client.post(f"/api/v1/sessions/{session_id}/messages", json={"question": "下一步补什么证据？"})
    assert answer.status_code == 200
    assert answer.json()["context_session_id"] == session_id
    history = client.get(f"/api/v1/sessions/{session_id}/messages").json()
    assert [item["role"] for item in history] == ["user", "assistant"]


def test_score_and_memo_use_the_current_target_card() -> None:
    created = client.post("/api/v1/sessions", json={"question": "JAK2 in myeloproliferative neoplasms: is a small molecule program worth validating?"})
    assert created.status_code == 201
    session_id = created.json()["id"]
    assert client.post(f"/api/v1/sessions/{session_id}/research", json={"question": created.json()["question"]}).status_code == 202

    score = client.get(f"/api/v1/sessions/{session_id}/scores")
    memo = client.post(f"/api/v1/sessions/{session_id}/decision-memos")
    assert score.status_code == 200
    assert score.json()["manual_review_required"] is True
    assert memo.status_code == 200
    assert "JAK2" in memo.json()["projectDefinition"]


def test_event_cursor_skips_already_seen_events() -> None:
    response = client.get("/api/v1/sessions/session-ror1/events", headers={"Last-Event-ID": "2"})
    assert response.status_code == 200
    assert "id: 1" not in response.text
    assert "id: 3" in response.text
