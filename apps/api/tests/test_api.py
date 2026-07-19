from fastapi.testclient import TestClient

from app.main import app
from app.services.research.card_builder import build_target_card, infer_scope
from app.services.research.connectors import ConnectorResult, EvidenceHit, ResearchBundle


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


def test_infer_scope_normalizes_lowercase_target_input() -> None:
    target, disease, modality = infer_scope("jak2 在骨髓增殖性肿瘤中是否适合开发小分子？")
    assert target == "JAK2"
    assert disease == "骨髓增殖性肿瘤"
    assert modality == "小分子"


def test_infer_scope_accepts_short_lowercase_target_input() -> None:
    target, _, _ = infer_scope("靶点身份：确认标准实体、别名和蛋白关系 jak")
    assert target == "JAK"


def test_infer_scope_resolves_drug_alias_to_biological_target() -> None:
    target, disease, modality = infer_scope("正大天晴获得 KRAS G12C 靶向药物 D-1553 在中国大陆的独家许可")
    assert target == "KRAS"
    assert disease is None
    assert modality == "小分子"


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
    assert [step["label"] for step in card["metadata"]["workflow"]] == ["实体归一", "权威数据库", "文献与临床", "证据整合"]

    answer = client.post(f"/api/v1/sessions/{session_id}/messages", json={"question": "下一步补什么证据？"})
    assert answer.status_code == 200
    assert answer.json()["context_session_id"] == session_id
    history = client.get(f"/api/v1/sessions/{session_id}/messages").json()
    assert [item["role"] for item in history] == ["user", "user", "assistant"]
    assert history[0]["content"] == created.json()["question"]


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
    assert [item["label"] for item in memo.json()["radar"]] == ["临床需求", "靶点验证", "竞争格局", "风险可控性（近期预警反向）", "患者分层可执行性"]
    assert len(memo.json()["riskAlerts"]) == 5


def test_decision_memo_trigger_question_is_kept_in_session_history() -> None:
    created = client.post("/api/v1/sessions", json={"question": "EGFR 在 NSCLC 中的证据成熟度如何？"})
    session_id = created.json()["id"]
    assert client.post(f"/api/v1/sessions/{session_id}/research", json={"question": created.json()["question"]}).status_code == 202
    memo = client.post(f"/api/v1/sessions/{session_id}/decision-memos", json={"question": "生成差异化建议"})
    assert memo.status_code == 200
    stored = client.get(f"/api/v1/sessions/{session_id}/decision-memos")
    assert stored.status_code == 200
    assert stored.json()["projectDefinition"].startswith("围绕 EGFR")
    assert stored.json()["triggerQuestion"] == "生成差异化建议"
    assert stored.json()["createdAt"]
    history = client.get(f"/api/v1/sessions/{session_id}/messages").json()
    assert history[-1]["content"] == "生成差异化建议"


def test_assistant_message_keeps_question_reference() -> None:
    session = client.post("/api/v1/sessions", json={"question": "EGFR 在肺癌中的临床进展是什么？"}).json()
    session_id = session["id"]
    response = client.post(f"/api/v1/sessions/{session_id}/messages", json={"question": "请只回答临床进展"})
    assert response.status_code == 200
    history = client.get(f"/api/v1/sessions/{session_id}/messages").json()
    user = next(item for item in reversed(history) if item["role"] == "user" and item["content"] == "请只回答临床进展")
    assistant = next(item for item in reversed(history) if item["role"] == "assistant")
    assert assistant["reply_to"] == user["id"]


def test_card_deduplicates_repeated_structured_function_annotations() -> None:
    duplicate_hits = [
        EvidenceHit(id=f"uniprot:{index}", connector="uniprot", source_type="structured_database", title="Tyrosine-protein kinase JAK2", url="https://www.uniprot.org/", summary="JAK2")
        for index in range(3)
    ]
    card = build_target_card(
        "session-dedup",
        "JAK2 在 MPN 中的功能？",
        ResearchBundle(target="JAK2", disease="MPN", modality="小分子", connectors=[ConnectorResult(connector="uniprot", status="READY", items=duplicate_hits)], items=duplicate_hits, graph_nodes=[], graph_relations=[]),
        is_mock=True,
    )
    assert card["biology"]["functions"] == ["Tyrosine-protein kinase JAK2"]


def test_card_uses_official_company_program_stage_without_calling_it_a_trial() -> None:
    announcement = EvidenceHit(
        id="company_announcement:sse:20241111:d1553",
        connector="company_news",
        source_type="regulatory_announcement",
        title="格索雷塞片获 NMPA 批准上市",
        url="https://example.com/d1553",
        summary="官方公告确认格索雷塞（D-1553）获批上市。",
        metadata={"published_at": "2024-11-11", "stage": "MARKETED", "drug_name": "格索雷塞（D-1553）", "sponsor": "益方生物 × 正大天晴"},
    )
    bundle = ResearchBundle(target="KRAS", disease=None, modality="小分子", connectors=[ConnectorResult(connector="company_news", status="READY", items=[announcement]), ConnectorResult(connector="clinicaltrials", status="DEGRADED", error="request failed")], items=[announcement], graph_nodes=[], graph_relations=[])
    card = build_target_card("session-kras", "KRAS G12C 的 D-1553 最新状态？", bundle, is_mock=False)
    assert card["metrics"]["highestClinicalStage"] == "已获批上市（中国）"
    assert card["trials"] == []
    assert card["drugs"][0]["name"] == "格索雷塞（D-1553）"
    assert card["drugs"][0]["stage"] == "已获批上市"


def test_card_merges_company_program_updates_and_keeps_highest_stage() -> None:
    phase_two = EvidenceHit(
        id="company_announcement:hkex:20230803:d1553",
        connector="company_news",
        source_type="company_announcement",
        title="D-1553 独家许可",
        url="https://example.com/license",
        summary="许可披露时处于 II 期",
        metadata={"stage": "PHASE_2", "drug_name": "格索雷塞（D-1553）", "sponsor": "益方生物 × 正大天晴"},
    )
    marketed = EvidenceHit(
        id="company_announcement:sse:20241111:d1553",
        connector="company_news",
        source_type="regulatory_announcement",
        title="格索雷塞获批上市",
        url="https://example.com/approval",
        summary="NMPA 批准上市",
        metadata={"stage": "MARKETED", "drug_name": "格索雷塞（D-1553）", "sponsor": "益方生物 × 正大天晴"},
    )
    bundle = ResearchBundle(
        target="KRAS",
        disease=None,
        modality="小分子",
        connectors=[ConnectorResult(connector="company_news", status="READY", items=[phase_two, marketed])],
        items=[phase_two, marketed],
        graph_nodes=[],
        graph_relations=[],
    )
    card = build_target_card("session-kras-merge", "KRAS G12C D-1553", bundle, is_mock=False)
    assert card["drugs"][0]["stage"] == "已获批上市"
    assert card["drugs"][0]["sourceIds"] == [marketed.id, phase_two.id]


def test_event_cursor_skips_already_seen_events() -> None:
    response = client.get("/api/v1/sessions/session-ror1/events", headers={"Last-Event-ID": "2"})
    assert response.status_code == 200
    assert "id: 1" not in response.text
    assert "id: 3" in response.text
