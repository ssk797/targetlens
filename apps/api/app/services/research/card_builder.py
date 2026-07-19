"""Build a TargetLens target card from normalized public-source hits.

The card builder deliberately keeps claims conservative.  A connector result is
evidence that a record was found, not proof of efficacy or a development
recommendation.  This boundary is important when a connector is empty or
degraded and makes the UI useful for targets that are not part of the demo
dataset (for example JAK2).
"""

from __future__ import annotations

import re
from typing import Any

from app.services.research.connectors import EvidenceHit, ResearchBundle


TARGET_TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9-]{1,15})(?![A-Za-z0-9])")
TARGET_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "how", "in", "is", "it", "of", "on", "or", "the", "to", "what", "whether", "with", "worth",
    "target", "program", "project", "evidence", "research", "study", "trial", "therapy", "development", "判断", "靶点",
}
MODALITY_WORDS = {"adc", "car-t", "protac", "bispecific", "antibody", "small", "molecule", "small-molecule", "双抗", "单抗", "小分子"}


def _infer_target(normalized: str) -> str:
    """Resolve a target token from either ``JAK2`` or ``jak2`` user input.

    Gene symbols are often pasted in lowercase in chat.  We normalize the
    symbol before querying connectors, while keeping the original question in
    the session so the user's wording remains traceable.
    """

    candidates: list[tuple[int, int, str]] = []
    for index, match in enumerate(TARGET_TOKEN_PATTERN.finditer(normalized)):
        token = match.group(1)
        lower = token.lower()
        if lower in TARGET_STOP_WORDS or lower in MODALITY_WORDS:
            continue
        score = 0
        if token.isupper():
            score += 4
        if re.fullmatch(r"[a-z]{2,8}\d{1,4}(?:-[a-z0-9]+)?", lower):
            score += 7
        if any(character.isdigit() for character in token):
            score += 3
        if "-" in token:
            score += 1
        # A short lowercase symbol (for example ``jak``) is still a valid
        # user-entered target. Keep the score deliberately low so a more
        # specific gene-like token such as ``jak2`` wins when both are present.
        if score == 0 and len(lower) >= 2:
            score = 1
        if score:
            candidates.append((score, -index, token))
    if not candidates:
        return "未解析靶点"
    return max(candidates)[2].upper()


def infer_scope(question: str) -> tuple[str, str | None, str]:
    """Infer a target, disease and modality from a natural-language question."""

    normalized = question.strip()
    target = _infer_target(normalized)

    modality = None
    for candidate in ("ADC", "双抗", "单抗", "小分子", "PROTAC", "CAR-T", "small molecule", "small-molecule", "antibody", "bispecific"):
        if candidate.lower() in normalized.lower():
            modality = {"small molecule": "小分子", "small-molecule": "小分子", "antibody": "抗体", "bispecific": "双抗"}.get(candidate, candidate)
            break

    disease: str | None = None
    patterns = (
        r"(?:在|针对|用于)([^，。！？?]{1,48}?)(?:中|里|患者|人群|是否|能否|适合)",
        r"([^，。！？?]{1,48}?)(?:患者|人群).{0,8}(?:靶点|治疗|开发)",
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            candidate = re.sub(r"^(?:靶点|研究|判断)\s*", "", match.group(1)).strip()
            if candidate and candidate != target:
                disease = candidate
                break

    if disease is None:
        english_match = re.search(r"\bin\s+([A-Za-z][A-Za-z0-9 -]{2,64}?)(?:\s*[:?]|\s+(?:is|are|for|whether)\b|$)", normalized, flags=re.IGNORECASE)
        if english_match:
            disease = english_match.group(1).strip()

    return target, disease, modality or "未指定"


def _tier(hit: EvidenceHit) -> str:
    return {
        "uniprot": "T1",
        "open_targets": "T1",
        "clinicaltrials": "T1",
        "chembl": "T1",
        "pubmed": "T2",
    }.get(hit.connector, "T3")


def _level(hit: EvidenceHit) -> str:
    return {
        "structured_database": "E2",
        "knowledge_graph": "E2",
        "compound_database": "E2",
        "literature": "E3",
        "clinical_trial": "E4",
    }.get(hit.source_type, "E3")


def _organization(hit: EvidenceHit) -> str:
    return {
        "uniprot": "UniProt",
        "open_targets": "Open Targets",
        "clinicaltrials": "ClinicalTrials.gov",
        "chembl": "ChEMBL",
        "pubmed": "PubMed / Europe PMC",
    }.get(hit.connector, hit.connector)


def _safe_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def _unique_texts(items: list[str], limit: int | None = None) -> list[str]:
    """Keep repeated connector labels from becoming repeated UI bullets.

    Structured authorities can describe the same normalized entity with an
    identical title. Those records remain available in ``validation`` for
    traceability, while the human-facing summary should not repeat the same
    sentence several times.
    """

    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = " ".join(str(item).split()).strip()
        key = normalized.casefold()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if limit is not None and len(result) >= limit:
            break
    return result


def _evidence(hit: EvidenceHit, disease: str | None) -> dict[str, Any]:
    published = hit.metadata.get("pubdate") or hit.metadata.get("firstPublicationDate")
    return {
        "id": hit.id,
        "level": _level(hit),
        "polarity": "SUPPORTS",
        "statement": _safe_text(hit.title, f"{hit.connector} 返回一条 {hit.source_type} 记录"),
        "studyType": hit.source_type,
        "disease": disease,
        "modelOrPopulation": _safe_text(hit.summary, "记录摘要未提供"),
        "limitations": ["本条记录由公共连接器自动归一化，仍需打开原文复核。"],
        "source": {
            "id": hit.id,
            "title": _safe_text(hit.title, hit.id),
            "organization": _organization(hit),
            "url": hit.url,
            "tier": _tier(hit),
            "publishedAt": str(published) if published else None,
            "retrievedAt": hit.fetched_at.isoformat(),
            "locator": hit.metadata.get("pmid") or hit.metadata.get("nct_id") or hit.metadata.get("accession"),
        },
        "reviewStatus": "AUTO_ACCEPTED" if _tier(hit) == "T1" else "PENDING",
    }


def build_target_card(
    session_id: str,
    question: str,
    bundle: ResearchBundle,
    data_cutoff: str | None = None,
    *,
    is_mock: bool = False,
) -> dict[str, Any]:
    """Convert a ``ResearchBundle`` into the frontend's stable card contract."""

    target = bundle.target
    disease = bundle.disease or "未指定适应证"
    modality = bundle.modality or "未指定"
    cutoff = data_cutoff or bundle.generated_at.date().isoformat()
    validation = [_evidence(item, bundle.disease) for item in bundle.items[:24]]
    if not validation:
        validation = [
            {
                "id": f"ev-{target.lower()}-no-record",
                "level": "E5",
                "polarity": "NEUTRAL",
                "statement": "当前检索未返回可用公开记录；这不等于该靶点不存在证据。",
                "studyType": "connector_status",
                "disease": bundle.disease,
                "modelOrPopulation": "需要扩大检索词或补充人工来源",
                "limitations": ["连接器为空或暂时降级，不能据此形成否定结论。"],
                "source": {
                    "id": f"ev-{target.lower()}-no-record",
                    "title": "TargetLens connector status",
                    "organization": "TargetLens",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={target}",
                    "tier": "T3",
                    "retrievedAt": bundle.generated_at.isoformat(),
                },
                "reviewStatus": "PENDING",
            }
        ]

    uniprot_hits = [item for item in bundle.items if item.connector == "uniprot"]
    open_targets_hits = [item for item in bundle.items if item.connector == "open_targets"]
    clinical_hits = [item for item in bundle.items if item.connector == "clinicaltrials"]
    chembl_hits = [item for item in bundle.items if item.connector == "chembl"]
    literature_hits = [item for item in bundle.items if item.connector == "pubmed"]
    identity_hit = uniprot_hits[0] if uniprot_hits else (open_targets_hits[0] if open_targets_hits else None)
    identity_name = identity_hit.title if identity_hit else target
    accession = next((str(item.metadata.get("accession")) for item in uniprot_hits if item.metadata.get("accession")), "未解析")

    degraded = [result.connector for result in bundle.connectors if result.status == "DEGRADED"]
    ready_connectors = sum(result.status == "READY" for result in bundle.connectors)
    total_connectors = max(len(bundle.connectors), 1)
    coverage = min(100, round(len(bundle.items) / max(total_connectors * 2, 1) * 100))
    stage = "未发现注册记录"
    if clinical_hits:
        phases = clinical_hits[0].metadata.get("phase") or []
        stage = ", ".join(str(phase) for phase in phases) if phases else "已发现注册记录"

    graph_edges = [
        {
            "source": relation.source,
            "target": relation.target,
            "relation": relation.predicate,
            "evidenceIds": relation.evidence_ids,
        }
        for relation in bundle.graph_relations
    ]
    graph_nodes = [{"id": node.id, "label": node.label, "type": node.type} for node in bundle.graph_nodes]
    source_names = ", ".join(_unique_texts([_organization(item) for item in bundle.items[:3]], limit=3)) or "暂无返回来源"
    connector_note = f"；降级来源：{', '.join(degraded)}" if degraded else ""
    connector_status = "DEGRADED" if degraded else ("READY" if bundle.connectors else "PENDING")
    workflow = [
        {
            "id": "entity-resolution",
            "label": "实体归一",
            "status": "READY",
            "detail": f"已识别 {target}",
        },
        {
            "id": "authoritative-sources",
            "label": "权威数据库",
            "status": connector_status,
            "detail": f"{ready_connectors}/{total_connectors} 个连接器返回",
        },
        {
            "id": "literature-retrieval",
            "label": "文献与临床",
            "status": "READY" if literature_hits or clinical_hits else ("PARTIAL" if bundle.items else "PENDING"),
            "detail": f"{len(literature_hits)} 篇文献 · {len(clinical_hits)} 条试验",
        },
        {
            "id": "evidence-integration",
            "label": "证据整合",
            "status": "READY" if validation else "PENDING",
            "detail": f"生成 {len(validation)} 条可追溯证据",
        },
    ]
    mechanism = _unique_texts(
        [
            f"{target} → 结构化注释",
            "公开文献与临床记录交叉核验",
            "把适应证和药物形式作为独立边界",
        ],
        limit=3,
    )
    function_annotations = _unique_texts([item.title for item in (uniprot_hits + open_targets_hits)], limit=4)
    if not function_annotations:
        function_annotations = ["暂无结构化功能注释"]
    dispute_notes = _unique_texts([f"{name} 未返回可用记录" for name in degraded], limit=3)
    if not dispute_notes:
        dispute_notes = ["本卡不把关联性记录解释为因果证明。"]

    executive_summary = (
        f"{target} 的实时检索已覆盖 {ready_connectors}/{total_connectors} 个来源，返回 {len(bundle.items)} 条记录（{source_names}）。"
        f" 这些记录支持继续做范围明确的验证，但不能单独替代药理、毒理、临床或监管判断{connector_note}。"
    )

    modality_options = [modality]
    for option in ("小分子", "抗体", "ADC"):
        if option not in modality_options:
            modality_options.append(option)
    modality_options = modality_options[:3]
    druggability = [
        {
            "modality": option,
            "fit": "MEDIUM" if option == modality and bundle.items else "INSUFFICIENT",
            "evidence": f"当前归一化结果 {len(bundle.items)} 条，尚未完成形式特异性验证。",
            "limitation": "公开记录不能直接证明可开发性或治疗窗。",
            "verify": "补充结合、内吞、药效和正常组织窗口实验。",
        }
        for option in modality_options
    ]

    trials = [
        {
            "identifier": str(item.metadata.get("nct_id", item.id.split(":")[-1])),
            "title": item.title,
            "phase": ", ".join(str(phase) for phase in (item.metadata.get("phase") or [])) or "未报告",
            "status": item.summary,
            "sourceId": item.id,
        }
        for item in clinical_hits[:8]
    ]
    drugs = [
        {
            "name": item.title,
            "sponsor": "ChEMBL 公共条目",
            "modality": "化合物",
            "stage": "非临床线索",
            "status": "已检索",
            "note": item.summary,
            "sourceIds": [item.id],
        }
        for item in chembl_hits[:8]
    ]
    if not drugs:
        drugs = [{"name": "暂无可归一化药物项目", "sponsor": "—", "modality": modality, "stage": "未知", "status": "待补充", "note": "当前来源未返回可用项目记录。", "sourceIds": [validation[0]["id"]]}]

    risk_source = validation[0]["id"]
    risk_text = "来源覆盖或正常组织窗口仍需人工复核"
    risks = [
        {
            "id": f"risk-{target.lower()}-review",
            "severity": "R3" if bundle.items else "R4",
            "type": "证据边界",
            "title": "不能从当前检索直接推出开发结论",
            "scope": "本次公开来源范围",
            "fact": risk_text,
            "impact": "建议等级受证据完整性限制",
            "sourceId": risk_source,
            "review": "补充原文、实验和安全性证据后复核",
            "mitigable": True,
        }
    ]
    conclusion = (
        f"{target} 可进入下一轮分层验证，但当前结果不足以直接判定其在 {disease} 中适合开发 {modality}。"
        if bundle.items
        else f"{target} 当前未获得足够公开证据，不能据此判定其在 {disease} 中适合开发 {modality}。"
    )

    return {
        "id": f"card-{target.lower().replace(' ', '-')}-{session_id[-8:]}-v1",
        "sessionId": session_id,
        "version": 1,
        "target": {"symbol": target, "name": identity_name, "aliases": [], "uniprotId": accession},
        "scope": {"disease": disease, "modality": modality, "question": question},
        "metrics": {
            "evidenceMaturity": f"{'中等' if len(bundle.items) >= 3 else '初步'} · {'E3' if literature_hits else 'E2'}",
            "highestClinicalStage": stage,
            "primaryModality": modality,
            "riskStatus": "部分来源降级 · 需复核" if degraded else ("需人工复核" if bundle.items else "证据不足"),
            "competition": f"{len(chembl_hits)} 条化合物线索" if chembl_hits else "待补充竞争检索",
            "citationCoverage": f"{coverage}% · {'实时来源' if not is_mock else '本地测试'}",
        },
        "executiveSummary": executive_summary,
        "biology": {
            "summary": f"{identity_name} 的结构化注释与公开文献已按 {target} 汇总；具体机制仍需回到原始记录核验。",
            "mechanism": mechanism,
            "functions": function_annotations,
            "disputes": dispute_notes,
        },
        "expression": {
            "summary": "当前连接器未提供可直接替代表达谱分析的完整人群数据，需补充组织与患者分层证据。",
            "tumorSignals": [{"label": disease, "level": "证据不足", "note": "需要疾病特异性表达与依赖性数据"}],
            "normalTissue": ["正常组织窗口未在本次检索中完成定量复核"],
            "population": ["患者亚群和检测阈值待定义"],
        },
        "validation": validation,
        "druggability": druggability,
        "drugs": drugs,
        "trials": trials,
        "competition": {
            "summary": "竞争判断仅基于本次公开来源命中，不能视为完整管线盘点。",
            "signals": [f"{len(literature_hits)} 条文献记录", f"{len(clinical_hits)} 条临床登记", f"{len(chembl_hits)} 条化合物记录"],
            "whitespace": "先补齐同靶点项目、适应证和分层标志物，再判断差异化空间。",
        },
        "risks": risks,
        "graph": {"nodes": graph_nodes, "edges": graph_edges},
        "conclusions": {
            "verdict": conclusion,
            "boundaries": ["来源命中不等于疗效证明", "需要区分靶点、适应证和药物形式的证据"],
            "unknowns": ["正常组织安全窗口", "可重复的患者分层标志物", "形式特异性药效与竞争格局"],
        },
        "metadata": {
            "isMock": is_mock,
            "generatedForDemo": is_mock,
            "dataCutoff": cutoff,
            "disclaimer": "实时公共来源已归一化展示；本卡不替代药理、毒理、临床或监管判断。",
            "workflow": workflow,
        },
    }


def demo_bundle(target: str, disease: str | None, modality: str | None) -> ResearchBundle:
    """Return an explicit empty bundle for offline tests, never a fake target claim."""

    return ResearchBundle(target=target, disease=disease, modality=modality, connectors=[], items=[], graph_nodes=[], graph_relations=[])
