import asyncio
import hashlib
import json
import logging
from collections.abc import AsyncIterator
from datetime import date
from typing import Any, Literal, cast
from uuid import UUID, uuid4

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.logging import configure_logging
from app.schemas import (
    DatabaseStatus,
    DecisionMemoRequest,
    HealthResponse,
    MessageCreate,
    ReportCreate,
    ResearchJob,
    ResearchPreviewRequest,
    ResearchStart,
    Session,
    SessionCreate,
    SessionMessage,
    SessionPatch,
    now_utc,
)
from app.services.ai.deepseek import DeepSeekClient, DeepSeekProviderError
from app.services.research.card_builder import build_target_card, demo_bundle, infer_scope
from app.services.research.cache import cache_key, get_bundle as get_cached_bundle, put_bundle as put_cached_bundle
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

logger = logging.getLogger(__name__)

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
SESSIONS: dict[str, Session] = {}
SESSION_MESSAGES: dict[str, list[SessionMessage]] = {}
# Keep the original ROR1 fixture available only for offline API tests.  A
# database-backed workspace must start empty and show only sessions the user
# actually created and searched.
if settings.api_mode != "database":
    SESSIONS["session-ror1"] = Session(
        id="session-ror1",
        title="ROR1 · ADC 立项判断",
        question="ROR1 在三阴性乳腺癌中是否适合开发 ADC？",
        status="READY",
        created_at=now_utc(),
        data_cutoff=DATA_CUTOFF,
        subtitle="三阴性乳腺癌 · 最近更新",
        updated_at=now_utc(),
        pinned=True,
        is_mock=False,
    )
    SESSION_MESSAGES["session-ror1"] = [
        SessionMessage(
            id="message-ror1-seed",
            session_id="session-ror1",
            role="user",
            content="ROR1 在三阴性乳腺癌中是否适合开发 ADC？",
            created_at=now_utc(),
            is_mock=False,
        )
    ]
TARGET_CARDS: dict[str, dict[str, Any]] = {}
RESEARCH_BUNDLES: dict[str, ResearchBundle] = {}
DECISION_MEMOS: dict[str, dict[str, Any]] = {}
LEGACY_ROR1_SESSION_ID = "00000000-0000-0000-0000-000000000001"


def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def _session_subtitle(question: str, status: str) -> str:
    target, disease, _ = infer_scope(question)
    scope = disease or "待补充适应证"
    suffix = "实时更新" if status == "READY" else ("检索中" if status == "PROCESSING" else "草稿")
    return f"{target} · {scope} · {suffix}"


def _session_with_defaults(session: Session) -> Session:
    return session.model_copy(
        update={
            "subtitle": session.subtitle or _session_subtitle(session.question, session.status),
            "updated_at": session.updated_at or session.created_at,
        }
    )


async def _db_list_sessions() -> list[Session]:
    if settings.api_mode != "database":
        return []
    try:
        from sqlalchemy import select

        from app.db.models.core import ResearchSession as DbResearchSession
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            rows = (await db.execute(select(DbResearchSession).order_by(DbResearchSession.updated_at.desc()))).scalars().all()
            return [
                Session(
                    id=str(row.id),
                    title=row.title,
                    question=row.question,
                    status=cast(Literal["READY", "PROCESSING", "DRAFT"], row.status if row.status in {"READY", "PROCESSING", "DRAFT"} else "DRAFT"),
                    created_at=row.created_at,
                    data_cutoff=row.data_cutoff,
                    subtitle=_session_subtitle(row.question, row.status),
                    updated_at=row.updated_at,
                    pinned=str(row.id) == LEGACY_ROR1_SESSION_ID,
                    is_mock=row.mode == "mock",
                )
                for row in rows
            ]
    except Exception:
        return []


async def _db_create_session(session: Session) -> None:
    if settings.api_mode != "database" or not _is_uuid(session.id):
        return
    try:
        from app.db.models.core import ResearchSession as DbResearchSession
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            db.add(
                DbResearchSession(
                    id=UUID(session.id),
                    title=session.title,
                    question=session.question,
                    status=session.status,
                    data_cutoff=session.data_cutoff,
                    mode="live" if not session.is_mock else "mock",
                    created_at=session.created_at,
                    updated_at=session.updated_at or session.created_at,
                )
            )
            await db.commit()
    except Exception:
        # The API remains usable when the optional database is temporarily down;
        # the health endpoint exposes that state and the in-memory cache keeps
        # the active task alive.
        return


async def _ensure_legacy_ror1_session() -> None:
    """Keep the original ROR1 record as historical navigation, not a fixture.

    New sessions are always researched from the submitted target. This one
    record is retained so existing users do not lose their earlier ROR1 work;
    its card is rebuilt from live connectors on first open when no card exists.
    """

    if settings.api_mode != "database":
        return
    try:
        from sqlalchemy import select

        from app.db.models.core import ResearchSession as DbResearchSession
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            exists = await db.scalar(select(DbResearchSession.id).where(DbResearchSession.id == UUID(LEGACY_ROR1_SESSION_ID)))
            if exists is not None:
                return
        session = Session(
            id=LEGACY_ROR1_SESSION_ID,
            title="ROR1 · ADC 立项判断",
            question="ROR1 在三阴性乳腺癌中是否适合开发 ADC？",
            status="READY",
            created_at=now_utc(),
            data_cutoff=DATA_CUTOFF,
            subtitle="三阴性乳腺癌 · 历史研读",
            updated_at=now_utc(),
            pinned=True,
            is_mock=False,
        )
        SESSIONS[session.id] = session
        SESSION_MESSAGES[session.id] = []
        await _db_create_session(session)
        await _ensure_initial_message(session)
    except Exception:
        return


async def _db_update_session(session: Session) -> None:
    if settings.api_mode != "database" or not _is_uuid(session.id):
        return
    try:
        from sqlalchemy import update

        from app.db.models.core import ResearchSession as DbResearchSession
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            await db.execute(
                update(DbResearchSession)
                .where(DbResearchSession.id == UUID(session.id))
                .values(status=session.status, title=session.title, question=session.question, updated_at=session.updated_at or now_utc())
            )
            await db.commit()
    except Exception:
        return


async def _db_delete_session(session_id: str) -> None:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return
    try:
        from sqlalchemy import delete

        from app.db.models.core import ResearchSession as DbResearchSession
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            await db.execute(delete(DbResearchSession).where(DbResearchSession.id == UUID(session_id)))
            await db.commit()
    except Exception:
        return


async def _db_save_message(message: SessionMessage) -> None:
    if settings.api_mode != "database" or not _is_uuid(message.session_id):
        return
    try:
        from app.db.models.core import SessionMessage as DbSessionMessage
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            metadata = {"provider": message.provider, "is_mock": message.is_mock}
            db.add(DbSessionMessage(id=UUID(message.id), session_id=UUID(message.session_id), role=message.role, content=message.content, citations=[metadata], created_at=message.created_at))
            await db.commit()
    except Exception:
        return


async def _db_update_message_timestamp(message_id: str, created_at: Any) -> None:
    if settings.api_mode != "database" or not _is_uuid(message_id):
        return
    try:
        from sqlalchemy import update

        from app.db.models.core import SessionMessage as DbSessionMessage
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            await db.execute(update(DbSessionMessage).where(DbSessionMessage.id == UUID(message_id)).values(created_at=created_at))
            await db.commit()
    except Exception:
        return


async def _ensure_initial_message(session: Session, *, is_mock: bool = False) -> None:
    """Persist the first user question as soon as a session exists.

    The old client kept this turn only in React state, so a page refresh made
    the opening question disappear from the history. Keeping it in the same
    message store as follow-up turns makes a session replayable even if the
    research job is still running or a connector later fails.
    """

    history = SESSION_MESSAGES.get(session.id)
    if history is None:
        history = await _db_list_messages(session.id)
        SESSION_MESSAGES[session.id] = history
    existing = next((item for item in history if item.role == "user" and item.content.strip() == session.question.strip()), None)
    if existing is not None:
        if existing.created_at > session.created_at:
            existing.created_at = session.created_at
            await _db_update_message_timestamp(existing.id, session.created_at)
            history.sort(key=lambda item: item.created_at)
        return
    message = SessionMessage(
        id=str(uuid4()),
        session_id=session.id,
        role="user",
        content=session.question,
        created_at=session.created_at,
        is_mock=is_mock,
    )
    history.insert(0, message)
    await _db_save_message(message)


async def _db_list_messages(session_id: str) -> list[SessionMessage]:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return []
    try:
        from sqlalchemy import select

        from app.db.models.core import SessionMessage as DbSessionMessage
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            rows = (await db.execute(select(DbSessionMessage).where(DbSessionMessage.session_id == UUID(session_id)).order_by(DbSessionMessage.created_at.asc()))).scalars().all()
            messages: list[SessionMessage] = []
            for row in rows:
                if row.role not in {"user", "assistant"}:
                    continue
                metadata = (row.citations or [{}])[0] if isinstance(row.citations, list) else {}
                messages.append(SessionMessage(id=str(row.id), session_id=session_id, role=cast(Literal["user", "assistant"], row.role), content=row.content, created_at=row.created_at, provider=metadata.get("provider"), is_mock=bool(metadata.get("is_mock", False))))
            return messages
    except Exception:
        return []


async def _db_save_card(session_id: str, card: dict[str, Any]) -> dict[str, Any]:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return card
    try:
        from sqlalchemy import desc, select

        from app.db.models.core import TargetCardVersion
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            latest = (await db.execute(select(TargetCardVersion.version).where(TargetCardVersion.session_id == UUID(session_id)).order_by(desc(TargetCardVersion.version)).limit(1))).scalar_one_or_none()
            version = int(latest or 0) + 1
            stored_card = {**card, "version": version}
            card_id = str(stored_card.get("id", ""))
            stored_card["id"] = f"{card_id.rsplit('-v', 1)[0]}-v{version}" if "-v" in card_id else card_id
            db.add(TargetCardVersion(session_id=UUID(session_id), version=version, status="READY", card=stored_card))
            await db.commit()
            return stored_card
    except Exception:
        return card


async def _db_load_card(session_id: str) -> dict[str, Any] | None:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return None
    try:
        from sqlalchemy import select

        from app.db.models.core import TargetCardVersion
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            row = (await db.execute(select(TargetCardVersion).where(TargetCardVersion.session_id == UUID(session_id)).order_by(TargetCardVersion.version.desc()))).scalars().first()
            return row.card if row else None
    except Exception:
        return None


async def _db_save_memo(session_id: str, memo: dict[str, Any]) -> dict[str, Any]:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return memo
    try:
        from sqlalchemy import desc, select

        from app.db.models.core import DecisionMemoVersion
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            latest = (
                await db.execute(
                    select(DecisionMemoVersion.version)
                    .where(DecisionMemoVersion.session_id == UUID(session_id))
                    .order_by(desc(DecisionMemoVersion.version))
                    .limit(1)
                )
            ).scalar_one_or_none()
            version = int(latest or 0) + 1
            db.add(DecisionMemoVersion(session_id=UUID(session_id), version=version, memo=memo))
            await db.commit()
    except Exception as exc:
        logger.warning("decision_memo_persist_failed", extra={"session_id": session_id, "error": str(exc)[:240]})
    return memo


async def _db_load_memo(session_id: str) -> dict[str, Any] | None:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return None
    try:
        from sqlalchemy import select

        from app.db.models.core import DecisionMemoVersion
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            row = (
                await db.execute(
                    select(DecisionMemoVersion)
                    .where(DecisionMemoVersion.session_id == UUID(session_id))
                    .order_by(DecisionMemoVersion.version.desc())
                    .limit(1)
                )
            ).scalars().first()
            return dict(row.memo) if row and isinstance(row.memo, dict) else None
    except Exception:
        return None


async def _db_save_bundle(session_id: str, bundle: ResearchBundle) -> None:
    """Persist source snapshots and relation facts for auditability.

    TargetCardVersion keeps the UI fast, while these rows make the same
    evidence reusable by later scoring, export and knowledge-graph stages.
    The operation is best-effort so a connector outage cannot erase an already
    usable card.
    """

    if settings.api_mode != "database" or not _is_uuid(session_id):
        return
    try:
        from sqlalchemy import delete, select

        from app.db.models.core import EvidenceItem as DbEvidenceItem
        from app.db.models.core import KnowledgeGraphFact, RelationFact, SessionContext, SourceRegistry, SourceSnapshot
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            await db.execute(delete(DbEvidenceItem).where(DbEvidenceItem.session_id == UUID(session_id)))
            await db.execute(delete(RelationFact).where(RelationFact.session_id == UUID(session_id)))
            for item in bundle.items:
                registry = (await db.execute(select(SourceRegistry).where(SourceRegistry.canonical_url == item.url))).scalars().first()
                if registry is None:
                    registry = SourceRegistry(canonical_url=item.url, title=item.title, source_type=item.source_type, authority_tier="T1" if item.connector in {"uniprot", "open_targets", "clinicaltrials", "chembl", "company_news"} else "T2")
                    db.add(registry)
                    await db.flush()
                payload = item.model_dump(mode="json")
                content_hash = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
                snapshot = SourceSnapshot(source_id=registry.id, content_hash=content_hash, payload=payload)
                db.add(snapshot)
                await db.flush()
                confidence = 0.85 if item.connector in {"uniprot", "open_targets", "clinicaltrials", "chembl", "company_news"} else 0.7
                db.add(DbEvidenceItem(session_id=UUID(session_id), source_snapshot_id=snapshot.id, evidence_type=item.source_type, claim=item.title, excerpt=item.summary, confidence=confidence, locator=item.metadata))
            for relation in bundle.graph_relations:
                db.add(RelationFact(session_id=UUID(session_id), subject=relation.source, predicate=relation.predicate, object=relation.target, evidence_ids=relation.evidence_ids))
            # Session relations are retained for audit history.  The same
            # normalized relations are also upserted into the reusable
            # first-party graph library so later target questions can enrich
            # their internal context without showing a graph card to users.
            graph_nodes = {node.id: node for node in bundle.graph_nodes}
            target_key = bundle.target.strip().lower()
            seen_relations: set[tuple[str, str, str, str]] = set()
            for relation in bundle.graph_relations:
                relation_key = (target_key, relation.source, relation.predicate, relation.target)
                if relation_key in seen_relations:
                    continue
                seen_relations.add(relation_key)
                subject_node = graph_nodes.get(relation.source)
                object_node = graph_nodes.get(relation.target)
                existing = (
                    await db.execute(
                        select(KnowledgeGraphFact).where(
                            KnowledgeGraphFact.target_key == target_key,
                            KnowledgeGraphFact.subject == relation.source,
                            KnowledgeGraphFact.predicate == relation.predicate,
                            KnowledgeGraphFact.object == relation.target,
                        )
                    )
                ).scalars().first()
                evidence_ids = list(dict.fromkeys(relation.evidence_ids or []))
                source_connectors = sorted({item.connector for item in bundle.items if item.id in evidence_ids})
                if existing is None:
                    db.add(
                        KnowledgeGraphFact(
                            target_key=target_key,
                            subject=relation.source,
                            subject_label=subject_node.label if subject_node else relation.source,
                            subject_type=subject_node.type if subject_node else "entity",
                            predicate=relation.predicate,
                            object=relation.target,
                            object_label=object_node.label if object_node else relation.target,
                            object_type=object_node.type if object_node else "entity",
                            evidence_ids=evidence_ids,
                            source_connectors=source_connectors,
                            first_seen_at=now_utc(),
                            last_seen_at=now_utc(),
                        )
                    )
                else:
                    existing.evidence_ids = list(dict.fromkeys([*(existing.evidence_ids or []), *evidence_ids]))
                    existing.source_connectors = list(dict.fromkeys([*(existing.source_connectors or []), *source_connectors]))
                    existing.last_seen_at = now_utc()
            context = (await db.execute(select(SessionContext).where(SessionContext.session_id == UUID(session_id)))).scalars().first()
            connector_statuses = [{"connector": result.connector, "status": result.status, "error": result.error} for result in bundle.connectors]
            if context is None:
                db.add(SessionContext(session_id=UUID(session_id), context={"connector_statuses": connector_statuses}))
            else:
                context.context = {**(context.context or {}), "connector_statuses": connector_statuses}
            await db.commit()
    except Exception as exc:
        logger.warning("source_bundle_persist_failed", extra={"session_id": session_id, "error": str(exc)[:240]})
        return


async def _db_load_bundle(session_id: str, question: str) -> ResearchBundle | None:
    if settings.api_mode != "database" or not _is_uuid(session_id):
        return None
    try:
        from sqlalchemy import select

        from app.db.models.core import EvidenceItem as DbEvidenceItem
        from app.db.models.core import RelationFact, SessionContext, SourceRegistry, SourceSnapshot
        from app.services.research.connectors import ConnectorResult, EvidenceHit, GraphNode, GraphRelation
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            rows = (await db.execute(select(DbEvidenceItem, SourceSnapshot, SourceRegistry).join(SourceSnapshot, DbEvidenceItem.source_snapshot_id == SourceSnapshot.id).join(SourceRegistry, SourceSnapshot.source_id == SourceRegistry.id).where(DbEvidenceItem.session_id == UUID(session_id)))).all()
            relations = (await db.execute(select(RelationFact).where(RelationFact.session_id == UUID(session_id)))).scalars().all()
            context = (await db.execute(select(SessionContext).where(SessionContext.session_id == UUID(session_id)))).scalars().first()
            if not rows:
                return None
            hits: list[EvidenceHit] = []
            by_connector: dict[str, list[EvidenceHit]] = {}
            for _, snapshot, registry in rows:
                payload = snapshot.payload or {}
                try:
                    hit = EvidenceHit.model_validate(payload)
                except ValueError:
                    continue
                hits.append(hit)
                by_connector.setdefault(hit.connector, []).append(hit)
            target, disease, modality = infer_scope(question)
            target_node = f"target:{target.lower().replace(' ', '-')}"
            graph_nodes = [GraphNode(id=target_node, label=target, type="target")]
            if disease:
                disease_node = f"disease:{disease.lower().replace(' ', '-')}"
                graph_nodes.append(GraphNode(id=disease_node, label=disease, type="disease"))
            graph_relations = [GraphRelation(source=row.subject, predicate=row.predicate, target=row.object, evidence_ids=row.evidence_ids or []) for row in relations]
            for hit in hits:
                node_id = f"source:{hit.id}"
                graph_nodes.append(GraphNode(id=node_id, label=hit.title, type=hit.source_type))
            saved_statuses: dict[str, dict[str, Any]] = {}
            for item in ((context.context or {}).get("connector_statuses", []) if context else []):
                if isinstance(item, dict) and isinstance(item.get("connector"), str):
                    saved_statuses[item["connector"]] = item
            connector_names = list(dict.fromkeys([*saved_statuses.keys(), *by_connector.keys()]))
            connectors = [ConnectorResult(connector=name, status=saved_statuses.get(name, {}).get("status", "READY"), items=by_connector.get(name, []), error=saved_statuses.get(name, {}).get("error")) for name in connector_names]
            bundle = ResearchBundle(target=target, disease=disease, modality=modality, connectors=connectors, items=hits, graph_nodes=graph_nodes, graph_relations=graph_relations)
            return await _merge_graph_library(bundle)
    except Exception:
        return None


async def _db_load_graph_library(target: str) -> list[dict[str, Any]]:
    """Load reusable relations owned by TargetLens, never user-facing by default."""

    if settings.api_mode != "database":
        return []
    try:
        from sqlalchemy import select

        from app.db.models.core import KnowledgeGraphFact
        from app.db.session import SessionFactory

        async with SessionFactory() as db:
            rows = (await db.execute(select(KnowledgeGraphFact).where(KnowledgeGraphFact.target_key == target.strip().lower()))).scalars().all()
            return [
                {
                    "subject": row.subject,
                    "subject_label": row.subject_label,
                    "subject_type": row.subject_type,
                    "predicate": row.predicate,
                    "object": row.object,
                    "object_label": row.object_label,
                    "object_type": row.object_type,
                    "evidence_ids": list(row.evidence_ids or []),
                    "source_connectors": list(row.source_connectors or []),
                }
                for row in rows
            ]
    except Exception as exc:
        logger.info("knowledge_graph_library_read_failed", extra={"target": target, "error": str(exc)[:160]})
        return []


async def _merge_graph_library(bundle: ResearchBundle) -> ResearchBundle:
    """Merge prior first-party graph facts into the internal bundle context."""

    facts = await _db_load_graph_library(bundle.target)
    if not facts:
        return bundle
    from app.services.research.connectors import GraphNode, GraphRelation

    nodes = {node.id: node for node in bundle.graph_nodes}
    relations = list(bundle.graph_relations)
    relation_keys = {(relation.source, relation.predicate, relation.target) for relation in relations}
    for fact in facts:
        subject = str(fact["subject"])
        target = str(fact["object"])
        nodes.setdefault(subject, GraphNode(id=subject, label=str(fact["subject_label"]), type=str(fact["subject_type"])))
        nodes.setdefault(target, GraphNode(id=target, label=str(fact["object_label"]), type=str(fact["object_type"])))
        key = (subject, str(fact["predicate"]), target)
        if key not in relation_keys:
            relations.append(GraphRelation(source=subject, predicate=key[1], target=target, evidence_ids=list(fact["evidence_ids"])))
            relation_keys.add(key)
    return bundle.model_copy(update={"graph_nodes": list(nodes.values()), "graph_relations": relations})


async def _fetch_research_bundle(
    target: str,
    disease: str | None,
    modality: str | None,
    *,
    force_refresh: bool = False,
    official_only: bool = False,
) -> ResearchBundle:
    """Fetch a normalized bundle, reusing Redis without hiding outages."""

    key = cache_key(target, disease, modality, official_only)
    if not force_refresh:
        cached = await get_cached_bundle(key)
        if cached is not None:
            return await _merge_graph_library(cached)

    bundle = await ResearchAggregator().search(target, disease, modality)
    if official_only:
        official_connectors = {"uniprot", "open_targets", "clinicaltrials", "chembl", "company_news"}
        connectors = [result for result in bundle.connectors if result.connector in official_connectors]
        items = [item for result in connectors for item in result.items]
        item_ids = {item.id for item in items}
        graph_nodes = [node for node in bundle.graph_nodes if node.type in {"target", "disease"} or node.id.removeprefix("source:") in item_ids]
        graph_relations = [relation for relation in bundle.graph_relations if not relation.evidence_ids or any(evidence_id in item_ids for evidence_id in relation.evidence_ids)]
        bundle = bundle.model_copy(update={"connectors": connectors, "items": items, "graph_nodes": graph_nodes, "graph_relations": graph_relations})
    # Do not retain an all-degraded response.  A partial bundle remains useful
    # and will be replaced on the next explicit refresh after the TTL expires.
    if bundle.items or not any(result.status == "DEGRADED" for result in bundle.connectors):
        await put_cached_bundle(key, bundle)
    return await _merge_graph_library(bundle)


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

    normalized_target, inferred_disease, inferred_modality = infer_scope(payload.target)
    target = normalized_target if normalized_target != "未解析靶点" else payload.target.strip()
    disease = payload.disease or inferred_disease
    modality = payload.modality or inferred_modality
    return await _fetch_research_bundle(target, disease, modality)


@app.get("/api/v1/sessions", response_model=list[Session])
async def list_sessions() -> list[Session]:
    await _ensure_legacy_ror1_session()
    db_sessions = await _db_list_sessions()
    for session in db_sessions:
        await _ensure_initial_message(session, is_mock=session.is_mock)
    merged = {session.id: _session_with_defaults(session) for session in SESSIONS.values()}
    merged.update({session.id: _session_with_defaults(session) for session in db_sessions})
    return list(merged.values())


@app.post("/api/v1/sessions", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate) -> Session:
    session_id = str(uuid4()) if settings.api_mode == "database" else f"session-{uuid4().hex[:8]}"
    target, disease, _ = infer_scope(payload.question)
    session = Session(
        id=session_id,
        title=f"{target} · {disease or '新建研读'}"[:48],
        question=payload.question,
        status="DRAFT",
        created_at=now_utc(),
        data_cutoff=DATA_CUTOFF,
        subtitle=_session_subtitle(payload.question, "DRAFT"),
        updated_at=now_utc(),
        is_mock=False,
    )
    SESSIONS[session_id] = session
    SESSION_MESSAGES[session_id] = []
    await _db_create_session(session)
    await _ensure_initial_message(session, is_mock=not (settings.ai_enabled or settings.api_mode == "database"))
    return _session_with_defaults(session)


@app.get("/api/v1/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str) -> Session:
    session = SESSIONS.get(session_id)
    if session is not None:
        return _session_with_defaults(session)
    db_sessions = await _db_list_sessions()
    session = next((item for item in db_sessions if item.id == session_id), None)
    if session is None:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    SESSIONS[session_id] = session
    await _ensure_initial_message(session, is_mock=session.is_mock)
    return _session_with_defaults(session)


@app.patch("/api/v1/sessions/{session_id}", response_model=Session)
async def patch_session(session_id: str, payload: SessionPatch) -> Session:
    session = await get_session(session_id)
    updates: dict[str, Any] = {"updated_at": now_utc()}
    if payload.title is not None:
        updates["title"] = payload.title.strip()
    if payload.pinned is not None:
        updates["pinned"] = payload.pinned
    updated = session.model_copy(update=updates)
    SESSIONS[session_id] = updated
    await _db_update_session(updated)
    return _session_with_defaults(updated)


@app.delete("/api/v1/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str) -> None:
    await get_session(session_id)
    SESSIONS.pop(session_id, None)
    SESSION_MESSAGES.pop(session_id, None)
    TARGET_CARDS.pop(session_id, None)
    RESEARCH_BUNDLES.pop(session_id, None)
    DECISION_MEMOS.pop(session_id, None)
    await _db_delete_session(session_id)


@app.post("/api/v1/sessions/{session_id}/research", response_model=ResearchJob, status_code=status.HTTP_202_ACCEPTED)
async def start_research(session_id: str, payload: ResearchStart | None = None) -> ResearchJob:
    session = await get_session(session_id)
    question = (payload.question if payload else None) or session.question
    session = session.model_copy(update={"question": question, "status": "PROCESSING", "subtitle": _session_subtitle(question, "PROCESSING"), "updated_at": now_utc()})
    SESSIONS[session_id] = session
    await _db_update_session(session)

    target, disease, modality = infer_scope(question)
    # Tests and an explicitly disabled AI environment stay offline.  The real
    # desktop configuration has AI_ENABLED=true, so it always uses public
    # connectors and never silently falls back to the ROR1 demo card.
    use_live_connectors = settings.ai_enabled or settings.api_mode == "database"
    await _ensure_initial_message(session, is_mock=not use_live_connectors)
    if use_live_connectors:
        bundle = await _fetch_research_bundle(
            target,
            disease,
            modality,
            force_refresh=bool(payload and payload.force_refresh),
            official_only=bool(payload and payload.official_only),
        )
    else:
        bundle = demo_bundle(target, disease, modality)
    card = build_target_card(session_id, question, bundle, DATA_CUTOFF, is_mock=not use_live_connectors)
    card = await _db_save_card(session_id, card)
    TARGET_CARDS[session_id] = card
    RESEARCH_BUNDLES[session_id] = bundle
    ready_session = session.model_copy(update={"status": "READY", "subtitle": _session_subtitle(question, "READY"), "updated_at": now_utc(), "is_mock": not use_live_connectors})
    SESSIONS[session_id] = ready_session
    await _db_update_session(ready_session)
    await _db_save_bundle(session_id, bundle)
    # Keep the queued contract for offline/test mode; the card is already
    # available in the cache, so the client can fetch it immediately.  Live
    # connector runs report READY after their normalized bundle is persisted.
    return ResearchJob(job_id=f"job-{uuid4().hex[:8]}", status="READY" if use_live_connectors else "QUEUED", events_url=f"/api/v1/sessions/{session_id}/events")


async def research_events(session_id: str, last_event_id: int = 0) -> AsyncIterator[str]:
    events = [
        ("research.progress", {"stage": "RESOLVING_ENTITY", "progress": 10}),
        ("research.progress", {"stage": "FETCHING_STRUCTURED_DATA", "progress": 35}),
        ("research.progress", {"stage": "RETRIEVING_LITERATURE", "progress": 58}),
        ("research.progress", {"stage": "BUILDING_GRAPH", "progress": 78}),
        ("research.section_ready", {"section": "biology"}),
        ("research.section_ready", {"section": "risks"}),
    ]
    session = await get_session(session_id)
    bundle = RESEARCH_BUNDLES.get(session_id) or await _db_load_bundle(session_id, session.question)
    if bundle:
        events.extend(("research.partial_failure", {"source": result.connector, "retryable": True, "error": result.error or "connector degraded"}) for result in bundle.connectors if result.status == "DEGRADED")
    card = TARGET_CARDS.get(session_id) or await _db_load_card(session_id)
    events.append(("research.completed", {"target_card_version": int(card.get("version", 1)) if card else 1, "session_id": session_id}))
    for index, (event_name, payload) in enumerate(events, start=1):
        if index <= last_event_id:
            continue
        await asyncio.sleep(0.08)
        yield f"id: {index}\nevent: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.get("/api/v1/sessions/{session_id}/events")
async def events(session_id: str, last_event_id: str | None = Header(default=None, alias="Last-Event-ID")) -> StreamingResponse:
    await get_session(session_id)
    try:
        cursor = max(int(last_event_id or "0"), 0)
    except ValueError:
        cursor = 0
    return StreamingResponse(research_events(session_id, cursor), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/v1/sessions/{session_id}/target-card")
async def target_card(session_id: str) -> dict[str, Any]:
    session = await get_session(session_id)
    card = TARGET_CARDS.get(session_id) or await _db_load_card(session_id)
    expected_target, expected_disease, expected_modality = infer_scope(session.question)
    stored_target = str((card or {}).get("target", {}).get("symbol", ""))
    stored_schema_version = int((card or {}).get("metadata", {}).get("schemaVersion", 1) or 1)
    # Older sessions could contain the unresolved demo card even after the
    # question had a recognizable lowercase target. Rebuild that stale card
    # from the current connectors instead of showing the placeholder forever.
    should_rebuild_card = card is not None and (
        (expected_target != "未解析靶点" and stored_target != expected_target)
        or stored_schema_version < 4
    )
    should_repair_title = expected_target != "未解析靶点" and session.title.startswith("未解析靶点")
    if should_rebuild_card or should_repair_title:
        if should_rebuild_card:
            card = None
        repaired_session = session.model_copy(
            update={
                "title": f"{expected_target} · {expected_disease or '新建研读'}"[:48],
                "subtitle": _session_subtitle(session.question, "READY"),
                "updated_at": now_utc(),
            }
        )
        SESSIONS[session_id] = repaired_session
        await _db_update_session(repaired_session)
        session = repaired_session
    if card is None:
        target, disease, modality = expected_target, expected_disease, expected_modality
        use_live_connectors = settings.ai_enabled or settings.api_mode == "database"
        bundle = await _fetch_research_bundle(target, disease, modality) if use_live_connectors else demo_bundle(target, disease, modality)
        card = build_target_card(session_id, session.question, bundle, DATA_CUTOFF, is_mock=not use_live_connectors)
        card = await _db_save_card(session_id, card)
        TARGET_CARDS[session_id] = card
        RESEARCH_BUNDLES[session_id] = bundle
        await _db_save_bundle(session_id, bundle)
    return card


@app.post("/api/v1/sessions/{session_id}/target-card/refresh")
async def refresh_target_card(session_id: str, payload: ResearchStart | None = None) -> dict[str, object]:
    """Refresh the current session without creating a second record."""

    await start_research(session_id, payload)
    return await target_card(session_id)


@app.get("/api/v1/evidence/{evidence_id}")
async def get_evidence(evidence_id: str) -> dict[str, Any]:
    for card in TARGET_CARDS.values():
        evidence = next((item for item in card.get("validation", []) if item.get("id") == evidence_id), None)
        if evidence is not None:
            return evidence
    if settings.api_mode == "database":
        try:
            from sqlalchemy import select

            from app.db.models.core import EvidenceItem as DbEvidenceItem
            from app.db.models.core import SourceRegistry, SourceSnapshot
            from app.db.session import SessionFactory

            async with SessionFactory() as db:
                row = (await db.execute(select(DbEvidenceItem, SourceSnapshot, SourceRegistry).join(SourceSnapshot, DbEvidenceItem.source_snapshot_id == SourceSnapshot.id).join(SourceRegistry, SourceSnapshot.source_id == SourceRegistry.id))).all()
                for evidence_item, snapshot, _ in row:
                    payload = snapshot.payload or {}
                    if payload.get("id") == evidence_id:
                        session = await get_session(str(evidence_item.session_id))
                        bundle = RESEARCH_BUNDLES.get(session.id) or await _db_load_bundle(session.id, session.question)
                        if bundle is not None:
                            card = build_target_card(session.id, session.question, bundle, DATA_CUTOFF, is_mock=session.is_mock)
                            evidence = next((item for item in card.get("validation", []) if item.get("id") == evidence_id), None)
                            if evidence is not None:
                                return evidence
                        return _evidence_from_hit_payload(payload)
        except Exception:
            pass
    raise HTTPException(status_code=404, detail="EVIDENCE_NOT_FOUND")


def _evidence_from_hit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep evidence returned by the DB compatible with the frontend card."""

    return payload


@app.get("/api/v1/sessions/{session_id}/evidence")
async def session_evidence(session_id: str) -> list[dict[str, Any]]:
    card = await target_card(session_id)
    return list(card.get("validation", []))


@app.get("/api/v1/sessions/{session_id}/graph")
async def session_graph(session_id: str) -> dict[str, Any]:
    card = await target_card(session_id)
    return dict(card.get("graph", {"nodes": [], "edges": []}))


@app.get("/api/v1/sessions/{session_id}/risks")
async def session_risks(session_id: str) -> list[dict[str, Any]]:
    card = await target_card(session_id)
    return list(card.get("risks", []))


@app.get("/api/v1/sessions/{session_id}/landscape")
async def session_landscape(session_id: str) -> dict[str, Any]:
    card = await target_card(session_id)
    return {"competition": card.get("competition", {}), "drugs": card.get("drugs", []), "trials": card.get("trials", [])}


@app.get("/api/v1/sessions/{session_id}/research-bundle", response_model=ResearchBundle)
async def session_research_bundle(session_id: str) -> ResearchBundle:
    session = await get_session(session_id)
    bundle = RESEARCH_BUNDLES.get(session_id)
    if bundle is not None:
        return bundle
    bundle = await _db_load_bundle(session_id, session.question)
    if bundle is not None:
        RESEARCH_BUNDLES[session_id] = bundle
        return bundle
    card = TARGET_CARDS.get(session_id) or await _db_load_card(session_id)
    if card is None:
        await target_card(session_id)
    bundle = RESEARCH_BUNDLES.get(session_id)
    if bundle is None:
        target, disease, modality = infer_scope(session.question)
        bundle = demo_bundle(target, disease, modality)
    return bundle


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


def score_request_for_card(card: dict[str, Any]) -> ScoreRequest:
    """Derive auditable score inputs from the current target card.

    These are deterministic heuristics for the first live scoring pass.  They
    never turn an evidence hit into a clinical claim; sparse or degraded cards
    lower confidence and keep the recommendation capped at ``PILOT``.
    """

    validation = list(card.get("validation", []))
    risks = list(card.get("risks", []))
    trials = list(card.get("trials", []))
    drugs = list(card.get("drugs", []))
    metadata = card.get("metadata", {})
    evidence_count = len(validation)
    real_evidence = sum(item.get("source", {}).get("tier") in {"T0", "T1"} for item in validation)
    degraded = "降级" in str(card.get("metrics", {}).get("riskStatus", "")) or "degraded" in str(card.get("executiveSummary", "")).lower()
    coverage = min(92, 30 + evidence_count * 3)
    authority = min(95, 45 + real_evidence * 4)
    consistency = min(88, 48 + min(evidence_count, 10) * 3)
    freshness = 78 if not metadata.get("isMock") else 45
    scope_clarity = 72 if card.get("scope", {}).get("disease") not in {None, "未指定适应症"} else 45

    redline_source = (risks[0].get("sourceId") if risks else None) or (validation[0].get("id") if validation else "")
    redlines = [
        RedlineInput(
            id=risks[0].get("id", "evidence-boundary") if risks else "evidence-boundary",
            name=risks[0].get("title", "关键证据仍需人工复核") if risks else "关键证据仍需人工复核",
            triggered=True,
            rationale=risks[0].get("impact", "公开来源不能替代实验、临床或监管判断") if risks else "当前证据不足以直接形成开发结论",
            evidence_ids=[redline_source] if redline_source else [],
            mitigable=True,
            requires_human_review=True,
            recommendation_cap="PILOT",
        )
    ]
    return ScoreRequest(
        opportunity=OpportunityDimensions(
            unmet_need=58,
            target_validation=min(88, 36 + evidence_count * 3),
            patient_selection=42 if scope_clarity < 60 else 58,
            modality_fit=55 if card.get("scope", {}).get("modality") not in {None, "未指定"} and evidence_count else 35,
            differentiation_space=max(32, 62 - len(drugs) * 5),
            clinical_feasibility=min(72, 30 + len(trials) * 8),
            safety_controllability=38,
        ),
        risk=RiskDimensions(
            normal_tissue_window=62,
            known_safety_class_risk=58,
            clinical_failure_risk=48 if trials else 64,
            regulatory_risk=38,
            scientific_uncertainty=max(38, 78 - evidence_count * 2),
            competitive_window=min(72, 34 + len(drugs) * 6),
        ),
        evidence=EvidenceDimensions(
            evidence_coverage=coverage,
            source_authority=authority,
            cross_source_consistency=consistency,
            freshness=freshness,
            scope_clarity=scope_clarity,
        ),
        redlines=redlines if degraded or evidence_count < 24 else [],
    )


@app.get("/api/v1/sessions/{session_id}/scores", response_model=ScoreResult)
async def get_scores(session_id: str) -> ScoreResult:
    await get_session(session_id)
    card = await target_card(session_id)
    return calculate_score(score_request_for_card(card))


@app.post("/api/v1/sessions/{session_id}/scores", response_model=ScoreResult)
async def calculate_session_scores(session_id: str, payload: ScoreRequest) -> ScoreResult:
    await get_session(session_id)
    return calculate_score(payload)


@app.post("/api/v1/sessions/{session_id}/messages")
async def ask(session_id: str, payload: MessageCreate) -> dict[str, object]:
    session = await get_session(session_id)
    question = payload.question.strip()
    history = SESSION_MESSAGES.get(session_id)
    if history is None:
        history = await _db_list_messages(session_id)
        SESSION_MESSAGES[session_id] = history
    user_message = SessionMessage(id=str(uuid4()), session_id=session_id, role="user", content=question, created_at=now_utc(), is_mock=False)
    history.append(user_message)
    await _db_save_message(user_message)

    card = TARGET_CARDS.get(session_id) or await _db_load_card(session_id)
    evidence_context = ""
    graph_context = ""
    if card:
        evidence = card.get("validation", [])[:6]
        evidence_context = "\n".join(f"- [{item.get('id', '')}] {item.get('statement', '')}（{item.get('source', {}).get('organization', '')}）" for item in evidence)
    bundle = RESEARCH_BUNDLES.get(session_id) or await _db_load_bundle(session_id, session.question)
    if bundle:
        graph_context = "\n".join(
            f"- {relation.source} --{relation.predicate}--> {relation.target}（证据：{', '.join(relation.evidence_ids) or '内部图谱'}）"
            for relation in bundle.graph_relations[:20]
        )
    context_messages = [
        {"role": "system", "content": (
            "你是 TargetLens 研究助手。你正在同一个持续会话中工作，必须记住并引用当前会话范围。"
            f"当前会话问题：{session.question}\n靶点卡证据摘要：{evidence_context or '尚未生成靶点卡'}\n"
            f"内部关系索引（只用于关联，不要向用户展示图谱）：{graph_context or '暂无可复用关系'}\n"
            "只把有证据支持的内容说成事实；无法确认时明确标注未知，不要编造文献、临床试验或监管结论。"
            "回答要直接回应本轮问题，并说明与上一轮的关系。使用中文 Markdown：结论用 **粗体**，复杂内容用小标题和项目符号；不要输出 HTML 或转义后的星号。"
        )}
    ]
    for item in history[-12:]:
        context_messages.append({"role": item.role, "content": item.content[-4000:]})
    provider = "mock"
    is_mock = True
    provider_status: str | None = None
    if settings.ai_enabled and settings.deepseek_api_key:
        try:
            client = DeepSeekClient.from_settings(settings)
            answer = await client.complete(
                context_messages,
                reasoning=payload.reasoning,
            )
            provider = "deepseek"
            is_mock = False
            summary = answer
            status_value = "READY"
        except DeepSeekProviderError:
            provider = "deepseek"
            provider_status = "DEGRADED"
            summary = f"**DeepSeek 暂时不可用。**\n\n围绕“{session.question}”的当前问题“{question}”，请先回到证据来源核验后再作判断。"
            status_value = "DEGRADED"
    else:
        summary = f"**当前仍在“{session.question}”这个研究范围内。**\n\n关于“{question}”，本地模型未启用；请结合靶点卡中的实时来源继续核验。"
        status_value = "PARTIAL"

    assistant_message = SessionMessage(id=str(uuid4()), session_id=session_id, role="assistant", content=summary, created_at=now_utc(), provider=provider, is_mock=is_mock)
    history.append(assistant_message)
    await _db_save_message(assistant_message)
    updated_session = session.model_copy(update={"updated_at": now_utc(), "subtitle": _session_subtitle(session.question, "READY")})
    SESSIONS[session_id] = updated_session
    await _db_update_session(updated_session)
    return {
        "id": assistant_message.id,
        "status": status_value,
        "summary": summary,
        "question": question,
        "data_cutoff": DATA_CUTOFF,
        "is_mock": is_mock,
        "provider": provider,
        "provider_status": provider_status,
        "context_session_id": session_id,
        "turn_index": len(history) // 2,
    }


@app.get("/api/v1/sessions/{session_id}/messages", response_model=list[SessionMessage])
async def list_messages(session_id: str) -> list[SessionMessage]:
    await get_session(session_id)
    history = SESSION_MESSAGES.get(session_id)
    if history is None:
        history = await _db_list_messages(session_id)
        SESSION_MESSAGES[session_id] = history
    return history


@app.get("/api/v1/sessions/{session_id}/decision-memos")
async def get_decision_memo(session_id: str) -> dict[str, Any] | None:
    await get_session(session_id)
    memo = DECISION_MEMOS.get(session_id) or await _db_load_memo(session_id)
    if memo is not None:
        DECISION_MEMOS[session_id] = memo
    return memo


@app.post("/api/v1/sessions/{session_id}/decision-memos")
async def generate_decision_memo(session_id: str, payload: DecisionMemoRequest | None = None) -> dict[str, Any]:
    session = await get_session(session_id)
    if payload and payload.question:
        history = SESSION_MESSAGES.get(session_id)
        if history is None:
            history = await _db_list_messages(session_id)
            SESSION_MESSAGES[session_id] = history
        user_message = SessionMessage(id=str(uuid4()), session_id=session_id, role="user", content=payload.question.strip(), created_at=now_utc(), is_mock=False)
        history.append(user_message)
        await _db_save_message(user_message)
        session = session.model_copy(update={"updated_at": now_utc()})
        SESSIONS[session_id] = session
        await _db_update_session(session)
    card = await target_card(session_id)
    target = card["target"]["symbol"]
    scope = card["scope"]
    unknowns = card["conclusions"].get("unknowns", [])
    validation = list(card.get("validation", []))
    drugs = list(card.get("drugs", []))
    trials = list(card.get("trials", []))
    risks = list(card.get("risks", []))
    disease_is_defined = scope.get("disease") not in {None, "", "未指定适应症"}
    evidence_count = len(validation)
    authoritative_count = sum(item.get("source", {}).get("tier") in {"T0", "T1"} for item in validation)
    degraded = "降级" in str(card.get("metrics", {}).get("riskStatus", "")) or bool(card.get("metadata", {}).get("isMock"))

    def bounded(value: float) -> int:
        return max(0, min(100, round(value)))

    radar = [
        {
            "label": "临床需求",
            "value": bounded(72 if disease_is_defined else 46),
            "note": "适应证已明确，仍需用未满足需求和现行标准治疗做定量对照。" if disease_is_defined else "尚未锁定适应证，先补充疾病场景和未满足需求。",
        },
        {
            "label": "靶点验证",
            "value": bounded(38 + min(evidence_count, 18) * 2.6 + min(authoritative_count, 8) * 2),
            "note": f"基于 {evidence_count} 条归一化证据（其中 {authoritative_count} 条来自 T1/T0 来源），不等于因果验证。",
        },
        {
            "label": "竞争格局",
            "value": bounded(84 - len(drugs) * 8 - len(trials) * 4),
            "note": f"当前返回 {len(drugs)} 条化合物线索、{len(trials)} 条临床登记；分数越高表示可探索空白越大。",
        },
        {
            "label": "风险可控性（近期预警反向）",
            "value": bounded(82 - len(risks) * 15 - (18 if degraded else 0)),
            "note": "分数越高表示当前检索暴露的风险压力越低；仍需持续追踪失败、监管和安全性信号。",
        },
        {
            "label": "患者分层可执行性",
            "value": bounded(35 + (22 if disease_is_defined else 0) + min(len(trials), 6) * 5),
            "note": "以适应证清晰度、临床登记和可落地检测路径估计，最终需回到患者样本验证。",
        },
    ]

    risk_alerts: list[str] = []
    risk_alerts.extend(f"{risk.get('severity', 'R3')} · {risk.get('title', '关键证据边界')}：{risk.get('fact', '需要人工复核')}" for risk in risks)
    risk_alerts.extend(str(item) for item in card.get("expression", {}).get("normalTissue", [])[:2])
    risk_alerts.extend(str(item) for item in card.get("expression", {}).get("population", [])[:2])
    risk_alerts.extend(str(item) for item in unknowns[:2])
    risk_alerts.extend(str(item) for item in card.get("competition", {}).get("signals", [])[:2])
    risk_alerts = risk_alerts[:5]
    while len(risk_alerts) < 5:
        risk_alerts.append("当前来源未覆盖该风险面，需补充权威记录后再下结论。")

    memo = {
        "projectDefinition": f"围绕 {target} 在 {scope['disease']} 中的 {scope['modality']} 研究假设，限定当前公开来源范围。",
        "whyNow": f"当前卡片已归一化 {len(card.get('validation', []))} 条证据，适合把下一步从泛泛讨论收敛到可验证问题。",
        "hardParts": ["证据强度与适用范围需要分开阅读", "正常组织窗口和患者分层仍未锁定", *unknowns[:1]],
        "options": [
            {"type": "VALIDATE", "title": "补齐关键验证证据", "content": "优先补充与适应证直接相关的机制、分层和安全窗口数据。", "evidenceIds": [item["id"] for item in card.get("validation", [])[:3]], "limitation": "公开来源不能替代实验与临床判断。", "priority": "P0", "cost": "中"},
            {"type": "COMPARE", "title": "做形式与竞争对照", "content": "把候选药物形式、同靶点项目和差异化终点放在同一张比较表。", "evidenceIds": [item["id"] for item in card.get("validation", [])[3:6]], "limitation": "当前竞争盘点不是完整管线。", "priority": "P1", "cost": "中"},
        ],
        "nextValidation": ["复核原始文献和结构化条目", "补充正常组织与患者分层证据", "定义可退出的药效/安全门槛"],
        "exitCriteria": ["关键证据无法重复", "安全窗口无法形成可测量阈值", "适应证和形式始终无法收敛"],
        "boundaries": card["conclusions"].get("boundaries", []),
        "radar": radar,
        "riskAlerts": risk_alerts,
    }
    DECISION_MEMOS[session_id] = memo
    return await _db_save_memo(session_id, memo)


@app.post("/api/v1/sessions/{session_id}/reports")
async def create_report(session_id: str, payload: ReportCreate | None = None) -> dict[str, Any]:
    card = await target_card(session_id)
    memo = await generate_decision_memo(session_id)
    lines = [
        f"# {card['target']['symbol']} 靶点研读报告",
        "",
        f"> {card['metadata']['disclaimer']}",
        "",
        f"- 研究范围：{card['scope']['disease']} · {card['scope']['modality']}",
        f"- 数据截至：{card['metadata']['dataCutoff']}",
        "",
        "## 结论",
        "",
        card["conclusions"]["verdict"],
        "",
        "## 证据",
        "",
        *[f"- [{item['level']}] {item['statement']}（{item['source']['organization']}）" for item in card.get("validation", [])],
        "",
        "## 下一步",
        "",
        *[f"- {item}" for item in memo["nextValidation"]],
    ]
    return {"filename": f"targetlens-{card['target']['symbol'].lower()}-research-report.md", "format": payload.format if payload else "markdown", "content": "\n".join(lines)}
