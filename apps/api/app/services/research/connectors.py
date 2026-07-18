from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, ClassVar

import httpx
from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceHit(BaseModel):
    id: str
    connector: str
    source_type: str
    title: str
    url: str
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=utcnow)


class ConnectorResult(BaseModel):
    connector: str
    status: str
    items: list[EvidenceHit] = Field(default_factory=list)
    error: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphRelation(BaseModel):
    source: str
    predicate: str
    target: str
    evidence_ids: list[str] = Field(default_factory=list)


class ResearchBundle(BaseModel):
    target: str
    disease: str | None = None
    modality: str | None = None
    generated_at: datetime = Field(default_factory=utcnow)
    connectors: list[ConnectorResult]
    items: list[EvidenceHit]
    graph_nodes: list[GraphNode]
    graph_relations: list[GraphRelation]


class ConnectorError(RuntimeError):
    pass


class BaseConnector:
    name: ClassVar[str]

    async def search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        raise NotImplementedError

    async def safe_search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        try:
            return await self.search(client, target, disease)
        except (ConnectorError, httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            return ConnectorResult(connector=self.name, status="DEGRADED", error=str(exc)[:240])

    async def get_json(self, client: httpx.AsyncClient, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ConnectorError(f"{self.name} request failed") from exc
        if not isinstance(payload, dict):
            raise ConnectorError(f"{self.name} returned an unexpected payload")
        return payload


class PubMedConnector(BaseConnector):
    name = "pubmed"

    async def search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        term = " AND ".join(part for part in (target, disease) if part)
        try:
            search = await self.get_json(client, "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={"db": "pubmed", "term": term, "retmode": "json", "retmax": 6})
        except ConnectorError:
            return await self._search_europe_pmc(client, term)
        ids = search.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return ConnectorResult(connector=self.name, status="EMPTY")
        summary = await self.get_json(client, "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
        result = summary.get("result", {})
        items = []
        for identifier in ids:
            record = result.get(identifier, {})
            items.append(EvidenceHit(id=f"pubmed:{identifier}", connector=self.name, source_type="literature", title=record.get("title", "PubMed record"), url=f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/", summary=record.get("sortfirstauthor", ""), metadata={"pmid": identifier, "journal": record.get("fulljournalname", ""), "pubdate": record.get("pubdate", "")}))
        return ConnectorResult(connector=self.name, status="READY", items=items)

    async def _search_europe_pmc(self, client: httpx.AsyncClient, term: str) -> ConnectorResult:
        payload = await self.get_json(client, "https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query": term, "format": "json", "pageSize": 6, "resultType": "core"})
        results = payload.get("resultList", {}).get("result", [])
        items = []
        for record in results:
            identifier = record.get("pmid") or record.get("id")
            if not identifier:
                continue
            pmid = record.get("pmid")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else f"https://europepmc.org/article/{record.get('source', 'MED')}/{identifier}"
            items.append(EvidenceHit(id=f"pubmed:{identifier}", connector=self.name, source_type="literature", title=record.get("title", "Europe PMC record"), url=url, summary=record.get("authorString", ""), metadata={"pmid": pmid, "journal": record.get("journalTitle", ""), "pubdate": record.get("firstPublicationDate", ""), "provider": "Europe PMC fallback"}))
        return ConnectorResult(connector=self.name, status="READY" if items else "EMPTY", items=items)


class ClinicalTrialsConnector(BaseConnector):
    name = "clinicaltrials"

    async def search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        query = " ".join(part for part in (target, disease) if part)
        payload = await self.get_json(client, "https://clinicaltrials.gov/api/v2/studies", params={"query.term": query, "pageSize": 6, "format": "json"})
        items = []
        for study in payload.get("studies", []):
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            nct_id = identification.get("nctId")
            if not nct_id:
                continue
            items.append(EvidenceHit(id=f"clinicaltrials:{nct_id}", connector=self.name, source_type="clinical_trial", title=identification.get("briefTitle", nct_id), url=f"https://clinicaltrials.gov/study/{nct_id}", summary=status_module.get("overallStatus", "STATUS_UNKNOWN"), metadata={"nct_id": nct_id, "phase": status_module.get("phase", [])}))
        return ConnectorResult(connector=self.name, status="READY" if items else "EMPTY", items=items)


class UniProtConnector(BaseConnector):
    name = "uniprot"

    async def search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        payload = await self.get_json(client, "https://rest.uniprot.org/uniprotkb/search", params={"query": f"gene:{target}", "format": "json", "size": 5})
        items = []
        for record in payload.get("results", []):
            accession = record.get("primaryAccession")
            if not accession:
                continue
            name = record.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", accession)
            items.append(EvidenceHit(id=f"uniprot:{accession}", connector=self.name, source_type="structured_database", title=name, url=f"https://www.uniprot.org/uniprotkb/{accession}/entry", summary=f"UniProt accession {accession}", metadata={"accession": accession, "gene": target}))
        return ConnectorResult(connector=self.name, status="READY" if items else "EMPTY", items=items)


class ChEMBLConnector(BaseConnector):
    name = "chembl"

    async def search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        payload = await self.get_json(client, "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json", params={"q": target, "limit": 5})
        items = []
        for record in payload.get("molecules", []):
            identifier = record.get("molecule_chembl_id")
            if not identifier:
                continue
            title = record.get("pref_name") or identifier
            items.append(EvidenceHit(id=f"chembl:{identifier}", connector=self.name, source_type="compound_database", title=title, url=f"https://www.ebi.ac.uk/chembl/explore/compound/{identifier}", summary=f"ChEMBL molecule {identifier}", metadata={"chembl_id": identifier}))
        return ConnectorResult(connector=self.name, status="READY" if items else "EMPTY", items=items)


class OpenTargetsConnector(BaseConnector):
    name = "open_targets"
    query = """
    query SearchTarget($queryString: String!) {
      search(queryString: $queryString) {
        total
        hits { id name entity }
      }
    }
    """

    async def search(self, client: httpx.AsyncClient, target: str, disease: str | None = None) -> ConnectorResult:
        try:
            response = await client.post("https://api.platform.opentargets.org/api/v4/graphql", json={"query": self.query, "variables": {"queryString": target}})
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ConnectorError("open_targets request failed") from exc
        if payload.get("errors"):
            raise ConnectorError("open_targets returned a GraphQL error")
        items = []
        for record in payload.get("data", {}).get("search", {}).get("hits", [])[:6]:
            identifier = record.get("id")
            if not identifier:
                continue
            items.append(EvidenceHit(id=f"open_targets:{identifier}", connector=self.name, source_type="knowledge_graph", title=record.get("name", identifier), url=f"https://platform.opentargets.org/app/target/{identifier}", summary=f"Open Targets {record.get('entity', 'entity')}", metadata={"entity": record.get("entity"), "target_id": identifier}))
        return ConnectorResult(connector=self.name, status="READY" if items else "EMPTY", items=items)


class ResearchAggregator:
    connectors: ClassVar[tuple[BaseConnector, ...]] = (PubMedConnector(), ClinicalTrialsConnector(), UniProtConnector(), ChEMBLConnector(), OpenTargetsConnector())

    async def search(self, target: str, disease: str | None = None, modality: str | None = None) -> ResearchBundle:
        timeout = httpx.Timeout(30.0, connect=8.0)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "TargetLens/0.2 research-connector"}) as client:
            # Run the research workflow in deliberate passes.  Structured
            # authorities resolve the entity first; literature and trial
            # registries then use that normalized target scope.  Each pass is
            # still concurrent internally, so one slow connector cannot block
            # its peers or erase a partial result.
            connector_by_name = {connector.name: connector for connector in self.connectors}
            ordered_passes = (
                ("uniprot", "open_targets", "chembl"),
                ("pubmed", "clinicaltrials"),
            )
            pass_results: list[ConnectorResult] = []
            for connector_names in ordered_passes:
                pass_results.extend(
                    await asyncio.gather(*(connector_by_name[name].safe_search(client, target, disease) for name in connector_names if name in connector_by_name))
                )
            results = pass_results
        items = [item for result in results for item in result.items]
        target_node = f"target:{target.lower().replace(' ', '-') }"
        graph_nodes = [GraphNode(id=target_node, label=target, type="target")]
        graph_relations: list[GraphRelation] = []
        if disease:
            disease_node = f"disease:{disease.lower().replace(' ', '-') }"
            graph_nodes.append(GraphNode(id=disease_node, label=disease, type="disease"))
            graph_relations.append(GraphRelation(source=target_node, predicate="studied_in", target=disease_node))
        for item in items:
            node_id = f"source:{item.id}"
            graph_nodes.append(GraphNode(id=node_id, label=item.title, type=item.source_type))
            graph_relations.append(GraphRelation(source=target_node, predicate="supported_by", target=node_id, evidence_ids=[item.id]))
        return ResearchBundle(target=target, disease=disease, modality=modality, connectors=results, items=items, graph_nodes=graph_nodes, graph_relations=graph_relations)
