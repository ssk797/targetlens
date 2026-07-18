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


class Session(BaseModel):
    id: str
    title: str
    question: str
    status: Literal["READY", "PROCESSING", "DRAFT"]
    created_at: datetime
    data_cutoff: str
    is_mock: bool = True


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
