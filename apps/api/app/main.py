import asyncio
import json
from collections.abc import AsyncIterator
from datetime import date
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.schemas import HealthResponse, ResearchJob, Session, SessionCreate, now_utc

app = FastAPI(title="TargetLens API", version="0.1.0", docs_url="/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

DATA_CUTOFF = date.today().isoformat()
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


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", mode="mock", timestamp=now_utc())


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


@app.post("/api/v1/sessions/{session_id}/messages")
async def ask(session_id: str, payload: dict[str, str]) -> dict[str, object]:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    question = payload.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=422, detail="QUESTION_REQUIRED")
    return {"id": f"answer-{uuid4().hex[:8]}", "status": "PARTIAL", "summary": "Mock grounded answer：请结合证据抽屉继续核验。", "question": question, "data_cutoff": DATA_CUTOFF, "is_mock": True}
