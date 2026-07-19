from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.services.auth import is_valid_email, normalize_email


DatabaseStatus = Literal["connected", "not_configured", "unavailable"]


class AuthRegister(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=200)
    display_name: str = Field(default="研究员", min_length=1, max_length=120)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        if not is_valid_email(normalized):
            raise ValueError("请输入有效的邮箱地址")
        return normalized

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        return value.strip() or "研究员"


class AuthLogin(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=1, max_length=200)
    remember: bool = False

    @field_validator("email")
    @classmethod
    def normalize_login_email(cls, value: str) -> str:
        return normalize_email(value)


class AuthUser(BaseModel):
    id: str
    email: str
    display_name: str


class AuthResponse(BaseModel):
    user: AuthUser


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
    # Assistant messages keep the user-message id they answer. This lets the
    # client replay a conversation in question/answer order even when a
    # provider response was persisted after a later user turn.
    reply_to: str | None = None


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
