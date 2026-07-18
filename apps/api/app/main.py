import asyncio
import json
from collections.abc import AsyncIterator
from datetime import date
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.logging import configure_logging
from app.schemas import DatabaseStatus, HealthResponse, MessageCreate, ResearchJob, ResearchPreviewRequest, Session, SessionCreate, now_utc
from app.services.ai.deepseek import DeepSeekClient, DeepSeekProviderError
from app.services.research.connectors import ResearchAggregator, ResearchBundle
from app.services.scoring.engine import calculate_score
from app.services.scoring.schemas import (
    EvidenceDimensions,
    OpportunityDimensions,
    RedlineInput,
    RiskDimensions,
    ScoreRequest,
    ScoreResult,
)

app = FastAPI(title="TargetLens API", version="0.1.0", docs_url="/docs")
configure_logging()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

DATA_CUTOFF = settings.data_cutoff or date.today().isoformat()
SESSIONS: dict[str, Session] = {
    "session-ror1": Session(
        id="session-ror1",
        title="ROR1 · ADC 立项判断",
        question="ROR1 在三阴性乳腺癌中是否适合开发 ADC？",
        status="READY",
        created_at=now_utc(),
        data_cutoff=DATA_CUTOFF,
    )
}


async def database_status() -> DatabaseStatus:
    if settings.api_mode != "database":
        return "not_configured"
    try:
        from sqlalchemy import text

        from app.db.session import engine

        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "unavailable"


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", mode=settings.api_mode, timestamp=now_utc(), database=await database_status())


@app.get("/api/v1/ai/status")
async def ai_status() -> dict[str, object]:
    configured = bool(settings.deepseek_api_key and settings.deepseek_api_key.get_secret_value().strip())
    return {
        "provider": "deepseek",
        "enabled": settings.ai_enabled,
        "configured": configured,
        "base_url": settings.deepseek_base_url,
        "models": {"fast": settings.deepseek_model_fast, "reasoning": settings.deepseek_model_reasoning},
    }


@app.post("/api/v1/research/preview", response_model=ResearchBundle)
async def research_preview(payload: ResearchPreviewRequest) -> ResearchBundle:
    """Fetch a normalized, traceable preview from public research connectors."""

    return await ResearchAggregator().search(payload.target, payload.disease, payload.modality)


@app.get("/api/v1/sessions", response_model=list[Session])
async def list_sessions() -> list[Session]:
    return list(SESSIONS.values())


@app.post("/api/v1/sessions", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate) -> Session:
    session_id = f"session-{uuid4().hex[:8]}"
    session = Session(
        id=session_id,
        title=payload.question[:32],
        question=payload.question,
        status="DRAFT",
        created_at=now_utc(),
        data_cutoff=DATA_CUTOFF,
    )
    SESSIONS[session_id] = session
    return session


@app.get("/api/v1/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str) -> Session:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return session


@app.post("/api/v1/sessions/{session_id}/research", response_model=ResearchJob, status_code=status.HTTP_202_ACCEPTED)
async def start_research(session_id: str) -> ResearchJob:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    SESSIONS[session_id] = session.model_copy(update={"status": "PROCESSING"})
    return ResearchJob(job_id=f"job-{uuid4().hex[:8]}", status="QUEUED", events_url=f"/api/v1/sessions/{session_id}/events")


async def research_events() -> AsyncIterator[str]:
    events = [
        ("research.progress", {"stage": "RESOLVING_ENTITY", "progress": 10}),
        ("research.progress", {"stage": "FETCHING_STRUCTURED_DATA", "progress": 35}),
        ("research.progress", {"stage": "RETRIEVING_LITERATURE", "progress": 58}),
        ("research.progress", {"stage": "BUILDING_GRAPH", "progress": 78}),
        ("research.section_ready", {"section": "biology"}),
        ("research.section_ready", {"section": "risks"}),
        ("research.completed", {"target_card_version": 1}),
    ]
    for index, (event_name, payload) in enumerate(events, start=1):
        await asyncio.sleep(0.08)
        yield f"id: {index}\nevent: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.get("/api/v1/sessions/{session_id}/events")
async def events(session_id: str) -> StreamingResponse:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return StreamingResponse(research_events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/v1/sessions/{session_id}/target-card")
async def target_card(session_id: str) -> dict[str, object]:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return {"id": "card-ror1-v1", "session_id": session_id, "version": 1, "metadata": {"isMock": True, "generatedForDemo": True, "dataCutoff": DATA_CUTOFF}}


def default_score_request() -> ScoreRequest:
    return ScoreRequest(
        opportunity=OpportunityDimensions(
            unmet_need=82,
            target_validation=74,
            patient_selection=78,
            modality_fit=72,
            differentiation_space=61,
            clinical_feasibility=58,
            safety_controllability=53,
        ),
        risk=RiskDimensions(
            normal_tissue_window=46,
            known_safety_class_risk=48,
            clinical_failure_risk=52,
            regulatory_risk=38,
            scientific_uncertainty=44,
            competitive_window=67,
        ),
        evidence=EvidenceDimensions(
            evidence_coverage=76,
            source_authority=81,
            cross_source_consistency=69,
            freshness=73,
            scope_clarity=78,
        ),
        redlines=[
            RedlineInput(
                id="target-expression-window",
                name="正常组织表达窗口需人工复核",
                triggered=True,
                rationale="现有来源提示表达窗口仍有异质性，不能直接视为可控。",
                evidence_ids=["ev-ror1-normal-tissue-01"],
                mitigable=True,
                requires_human_review=True,
                recommendation_cap="PILOT",
            )
        ],
    )


@app.get("/api/v1/sessions/{session_id}/scores", response_model=ScoreResult)
async def get_scores(session_id: str) -> ScoreResult:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return calculate_score(default_score_request())


@app.post("/api/v1/sessions/{session_id}/scores", response_model=ScoreResult)
async def calculate_session_scores(session_id: str, payload: ScoreRequest) -> ScoreResult:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return calculate_score(payload)


@app.post("/api/v1/sessions/{session_id}/messages")
async def ask(session_id: str, payload: MessageCreate) -> dict[str, object]:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    question = payload.question.strip()
    if settings.ai_enabled and settings.deepseek_api_key:
        try:
            client = DeepSeekClient.from_settings(settings)
            answer = await client.complete(
                [
                    {"role": "system", "content": "你是 TargetLens 研究助手。只把有证据支持的内容说成事实；无法确认时明确标注未知，不要编造文献、临床试验或监管结论。用简洁的中文回答。"},
                    {"role": "user", "content": question},
                ],
                reasoning=payload.reasoning,
            )
            return {"id": f"answer-{uuid4().hex[:8]}", "status": "READY", "summary": answer, "question": question, "data_cutoff": DATA_CUTOFF, "is_mock": False, "provider": "deepseek"}
        except DeepSeekProviderError:
            return {"id": f"answer-{uuid4().hex[:8]}", "status": "DEGRADED", "summary": "DeepSeek 暂时不可用，已回退到演示回答；请稍后重试。", "question": question, "data_cutoff": DATA_CUTOFF, "is_mock": True, "provider": "deepseek", "provider_status": "DEGRADED"}
    return {"id": f"answer-{uuid4().hex[:8]}", "status": "PARTIAL", "summary": "Mock grounded answer：请结合证据抽屉继续核验。", "question": question, "data_cutoff": DATA_CUTOFF, "is_mock": True}
