from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


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


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
