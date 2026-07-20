"""Small, best-effort Redis cache for normalized research bundles.

The cache is deliberately outside the connector implementations.  This keeps
each source connector responsible for parsing its own response while allowing
the API to reuse one complete, auditable bundle for repeated questions.
Redis is an optimization only: a cache outage must never turn a research
request into a fake result or prevent the database snapshot from being saved.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from app.core.config import settings
from app.services.research.connectors import ResearchBundle

logger = logging.getLogger(__name__)


def cache_key(target: str, disease: str | None, modality: str | None, official_only: bool = False) -> str:
    """Return a stable, non-sensitive key for a normalized research query."""

    payload = json.dumps(
        {
            "target": target.strip().upper(),
            "disease": (disease or "").strip().lower(),
            "modality": (modality or "").strip().lower(),
            "official_only": official_only,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    # Bump when connector coverage or normalization semantics change so old
    # bundles cannot mask newly added official-company evidence.
    return f"targetlens:research:v3:{digest}"


async def get_bundle(key: str) -> ResearchBundle | None:
    """Read a bundle from Redis, returning ``None`` for any cache failure."""

    if settings.api_mode != "database":
        return None
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        try:
            raw = await redis.get(key)
        finally:
            await redis.aclose()
        if not raw:
            return None
        return ResearchBundle.model_validate_json(raw)
    except Exception as exc:  # pragma: no cover - depends on optional runtime service
        logger.info("research_cache_read_failed", extra={"error": str(exc)[:160]})
        return None


async def put_bundle(key: str, bundle: ResearchBundle) -> None:
    """Store a normalized bundle with the configured TTL, best effort."""

    if settings.api_mode != "database":
        return
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        try:
            await redis.setex(key, settings.research_cache_ttl_seconds, bundle.model_dump_json())
        finally:
            await redis.aclose()
    except Exception as exc:  # pragma: no cover - depends on optional runtime service
        logger.info("research_cache_write_failed", extra={"error": str(exc)[:160]})


def cache_payload(bundle: ResearchBundle) -> dict[str, Any]:
    """Expose a small diagnostic shape without returning provider internals."""

    return {
        "target": bundle.target,
        "disease": bundle.disease,
        "modality": bundle.modality,
        "generated_at": bundle.generated_at,
        "items": len(bundle.items),
        "connectors": [{"connector": item.connector, "status": item.status, "items": len(item.items)} for item in bundle.connectors],
    }
