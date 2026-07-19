from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


DatabaseStatus = Literal["connected", "not_configured", "unavailable"]


class SessionCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class MessageCreate(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    official_only: bool = False
    reasoning: bool = False


class ResearchPreviewRequest(BaseModel):
    target: str = Field(min_length=1, max_length=200)
    disease: str | None = Field(default=None, max_length=200)
    modality: str | None = Field(default=None, max_length=100)


class ResearchStart(BaseModel):
    """Optional override used when starting a freshly-created session."""

    question: str | None = Field(default=None, min_length=1, max_length=4000)
    official_only: bool = False
    force_refresh: bool = False


class Session(BaseModel):
    id: str
    title: str
    question: str
    status: Literal["READY", "PROCESSING", "DRAFT"]
    created_at: datetime
    data_cutoff: str
    subtitle: str = ""
    updated_at: datetime | None = None
    pinned: bool = False
    is_mock: bool = True


class SessionPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    pinned: bool | None = None


class SessionMessage(BaseModel):
    id: str
    session_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    provider: str | None = None
    is_mock: bool = False


class ReportCreate(BaseModel):
    format: Literal["markdown"] = "markdown"


class DecisionMemoRequest(BaseModel):
    """Optional user prompt that triggered a persisted decision memo."""

    question: str | None = Field(default=None, min_length=1, max_length=4000)


class ResearchJob(BaseModel):
    job_id: str
    status: Literal["QUEUED", "RUNNING", "READY"]
    events_url: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    mode: str
    timestamp: datetime
    database: DatabaseStatus = "not_configured"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
