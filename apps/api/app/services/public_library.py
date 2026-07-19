"""Curated, read-only evidence snapshots that are safe to show publicly.

The public library is deliberately separate from research sessions.  It never
contains a user's question, session id, message history, graph facts, or
provider output.  Each snapshot is a compact teaching example assembled from
links to the original authoritative resources; it is not a substitute for a
fresh research run.
"""

from __future__ import annotations

from datetime import date

from app.schemas import (
    PublicLibraryEntry,
    PublicLibrarySection,
    PublicLibrarySource,
    PublicLibrarySummary,
    PublicLibraryTarget,
)


def _source(source_id: str, title: str, organization: str, url: str, license_note: str) -> PublicLibrarySource:
    return PublicLibrarySource(id=source_id, title=title, organization=organization, url=url, license=license_note)


def _section(key: str, title: str, summary: str, *points: str) -> PublicLibrarySection:
    return PublicLibrarySection(key=key, title=title, summary=summary, points=list(points))  # type: ignore[arg-type]


def public_library_entries(*, updated_at: str | None = None) -> list[PublicLibraryEntry]:
    """Return fresh model copies so callers cannot mutate the seed catalog."""

    cutoff = updated_at or date.today().isoformat()
    entries = [
        PublicLibraryEntry(
            slug="ror1",
            target=PublicLibraryTarget(symbol="ROR1", name="Receptor tyrosine kinase-like orphan receptor 1", aliases=["NTRK-like orphan receptor 1"]),
            headline="ROR1：从肿瘤表达窗口走向 ADC/双抗验证",
            summary="适合用来练习‘表达—成药—临床—失败风险’四步核查；公开快照不把研究假设写成临床结论。",
            updated_at=cutoff,
            sections=[
                _section("biology", "生物学功能", "受体型酪氨酸激酶样蛋白，发育期信号在成人组织中通常受限。", "参与 WNT/β-catenin 等发育和存活相关信号的研究。", "需要把结构域、配体关系与肿瘤细胞依赖性分开验证。"),
                _section("expression", "肿瘤表达", "多种血液瘤和实体瘤队列报告过异常表达，但组织和患者亚群差异明显。", "优先核对肿瘤样本、正常组织窗口和膜表面可及性。", "表达比例不能直接等同于药效人群比例。"),
                _section("drugability", "成药逻辑", "细胞表面可及性支持 ADC、双抗或细胞治疗等方向的探索。", "需要同时验证内吞、抗原密度、旁观者效应与正常组织安全窗。", "不同构型的暴露和毒性不可用同一条证据替代。"),
                _section("drugs", "代表药物", "公开开发项目主要集中在抗体偶联和免疫细胞重定向等模式。", "比较 payload、连接子、给药方案和入组生物标志物。", "项目名称、公司公告与注册状态需回到原始来源复核。"),
                _section("clinical", "临床进展", "公开临床信息需要按具体药物和适应症逐项检索，不能由靶点名推断阶段。", "将 ClinicalTrials.gov 试验记录与企业公告的开发阶段并列核验。", "阶段、状态和地区许可是不同字段。"),
                _section("risk", "失败与风险", "核心风险是正常组织表达窗口、抗原异质性和临床可转化性不足。", "把‘有表达’与‘有治疗窗’作为两条独立结论。", "下一步应优先补充患者分层和正常组织安全性证据。"),
            ],
            sources=[
                _source("uniprot-q01973", "ROR1 · UniProt Q01973", "UniProt", "https://www.uniprot.org/uniprotkb/Q01973/entry", "UniProt data: CC BY 4.0"),
                _source("opentargets-ror1", "ROR1 · Open Targets Platform", "Open Targets", "https://platform.opentargets.org/target/ENSG00000185483", "Open Targets platform licence applies"),
                _source("trials-ror1", "ROR1 · ClinicalTrials.gov search", "U.S. National Library of Medicine", "https://clinicaltrials.gov/search?term=ROR1", "ClinicalTrials.gov terms apply"),
            ],
            disclaimer="公开来源归一化示范快照；更新时间仅表示本快照生成时间，不代表实时注册结论。",
        ),
        PublicLibraryEntry(
            slug="jak2-mpn",
            target=PublicLibraryTarget(symbol="JAK2", name="Tyrosine-protein kinase JAK2", aliases=["JAK2 V617F", "Janus kinase 2"]),
            headline="JAK2 V617F：MPN 驱动突变与 JAK 抑制剂证据链",
            summary="用 MPN 场景示范如何把驱动突变、通路依赖、已上市药物与耐药风险分开判断。",
            updated_at=cutoff,
            sections=[
                _section("biology", "生物学功能", "JAK2 是细胞因子受体相关激酶，参与 JAK–STAT 信号转导。", "V617F 可导致激酶调控异常和持续信号活化。", "机制证据应区分突变本身、下游信号和疾病表型。"),
                _section("expression", "肿瘤表达", "MPN 中应优先讨论突变克隆和等位基因负荷，而不是泛化的‘表达升高’。", "真性红细胞增多症、原发性血小板增多症和骨髓纤维化的分层规则不同。", "检测平台、阈值和患者亚型会改变可比性。"),
                _section("drugability", "成药逻辑", "JAK1/2 或 JAK2 通路抑制可以缓解脾大和症状，但未必清除驱动克隆。", "比较选择性、骨髓抑制、感染风险和长期疾病修饰证据。", "‘通路抑制有效’与‘突变被根治’必须分开表述。"),
                _section("drugs", "代表药物", "代表性 JAK 抑制剂包括 ruxolitinib、fedratinib、pacritinib 和 momelotinib。", "每个药物的获批适应症、线次和安全性边界需要按监管标签核对。", "药物上市状态不能直接替代具体试验的入组和终点信息。"),
                _section("clinical", "临床进展", "JAK 抑制剂已形成 MPN 临床治疗基础，但不同疾病亚型的获益维度并不相同。", "优先比较脾脏反应、症状反应、血液学改善和总生存等终点。", "最新试验状态应以注册平台和监管/企业原始公告为准。"),
                _section("risk", "失败与风险", "主要风险包括耐药/复发、贫血和血小板减少、感染以及疾病进展。", "补充 JAK2 V617F 克隆负荷、替代通路和联合策略的直接证据。", "对 MPN 核心驱动突变的直接验证不能用非 MPN 线索替代。"),
            ],
            sources=[
                _source("uniprot-p52333", "JAK2 · UniProt P52333", "UniProt", "https://www.uniprot.org/uniprotkb/P52333/entry", "UniProt data: CC BY 4.0"),
                _source("opentargets-jak2", "JAK2 · Open Targets Platform", "Open Targets", "https://platform.opentargets.org/target/ENSG00000096968", "Open Targets platform licence applies"),
                _source("trials-jak2-mpn", "JAK2 MPN · ClinicalTrials.gov search", "U.S. National Library of Medicine", "https://clinicaltrials.gov/search?term=JAK2%20MPN", "ClinicalTrials.gov terms apply"),
            ],
            disclaimer="公开来源归一化示范快照；药品和临床状态必须按具体药物、适应症与地区标签复核。",
        ),
        PublicLibraryEntry(
            slug="kras-g12c",
            target=PublicLibraryTarget(symbol="KRAS", name="GTPase KRas", aliases=["KRAS G12C", "K-Ras"]),
            headline="KRAS G12C：突变选择性抑制与耐药演化",
            summary="用突变亚型示范靶点、药物、企业公告和注册状态如何交叉核验，避免把靶点阶段误当成药物阶段。",
            updated_at=cutoff,
            sections=[
                _section("biology", "生物学功能", "KRAS 是 RAS/MAPK 与 PI3K 等信号网络中的小 GTP 酶。", "G12C 改变核苷酸循环和下游信号依赖，具有突变选择性成药逻辑。", "需把突变蛋白机制与肿瘤组织背景共同考虑。"),
                _section("expression", "肿瘤表达", "KRAS G12C 是基因型标志物，不能按总 KRAS 蛋白表达筛选。", "非小细胞肺癌、结直肠癌和胰腺癌等适应症的频率和共突变不同。", "检测方法和变异等位基因比例影响人群定义。"),
                _section("drugability", "成药逻辑", "共价结合突变半胱氨酸并锁定非活化构象是 G12C 抑制的核心逻辑。", "反应深度、给药暴露、旁路激活和组织差异需要分别验证。", "单药反应不能推断所有 KRAS 亚型均可复制。"),
                _section("drugs", "代表药物", "代表性项目包括 sotorasib、adagrasib 以及在中国开发的 D-1553 等。", "药物是否获批、在何地区获批、许可方和商业化方要逐条回到监管或企业公告。", "企业授权公告可以补充开发/商业化信息，但不等于监管批准。"),
                _section("clinical", "临床进展", "KRAS G12C 已形成明确的临床开发赛道，阶段需按具体分子和适应症读取。", "并列记录注册试验、监管标签和企业最新披露，避免只看靶点聚合页。", "中国大陆许可、注册、生产和商业化权利属于交易字段，需单独标记。"),
                _section("risk", "失败与风险", "常见风险包括获得性耐药、旁路信号重激活、脑转移控制和联合毒性。", "把突变谱、共突变和治疗线次纳入患者分层。", "新闻稿、授权公告和临床注册记录的权威性与用途不同。"),
            ],
            sources=[
                _source("uniprot-p01116", "KRAS · UniProt P01116", "UniProt", "https://www.uniprot.org/uniprotkb/P01116/entry", "UniProt data: CC BY 4.0"),
                _source("opentargets-kras", "KRAS · Open Targets Platform", "Open Targets", "https://platform.opentargets.org/target/ENSG00000133703", "Open Targets platform licence applies"),
                _source("trials-kras-g12c", "KRAS G12C · ClinicalTrials.gov search", "U.S. National Library of Medicine", "https://clinicaltrials.gov/search?term=KRAS%20G12C", "ClinicalTrials.gov terms apply"),
            ],
            disclaimer="公开来源归一化示范快照；授权公告、药品注册与临床试验状态是三类不同事实，不能相互替代。",
        ),
        PublicLibraryEntry(
            slug="egfr-nsclc",
            target=PublicLibraryTarget(symbol="EGFR", name="Epidermal growth factor receptor", aliases=["ERBB1", "HER1"]),
            headline="EGFR：经典驱动靶点的分层治疗与耐药管理",
            summary="用 EGFR 示范成熟靶点仍需按突变亚型、药物代际和耐药机制逐层核对。",
            updated_at=cutoff,
            sections=[
                _section("biology", "生物学功能", "EGFR 是受体酪氨酸激酶，配体结合后驱动增殖和存活信号。", "RAS/RAF/MEK、PI3K/AKT 等下游通路共同决定表型。", "受体表达、驱动突变和配体依赖不是同一层面的证据。"),
                _section("expression", "肿瘤表达", "不同癌种可见 EGFR 扩增、过表达或激活突变，临床意义取决于具体分子事件。", "NSCLC 需要按 EGFR 变异类型和检测标准进行患者分层。", "免疫组化阳性不能直接等同于 TKI 敏感。"),
                _section("drugability", "成药逻辑", "ATP 竞争性小分子和抗体药物均有成熟开发路径。", "选择性、脑暴露、突变覆盖和野生型毒性是代际比较重点。", "获得性耐药后应重新检测分子机制。"),
                _section("drugs", "代表药物", "公开临床路径覆盖多代 EGFR TKI 与抗体/联合方案。", "比较适应症标签、脑转移活性、耐药后线次和真实世界可及性。", "同一药物在不同地区的批准状态可能不同。"),
                _section("clinical", "临床进展", "EGFR 已有成熟的监管和临床证据体系，但具体结论仍由分子亚型与线次决定。", "将注册试验终点、监管标签和指南版本分别记录。", "成熟赛道仍可能因耐药亚型和联合安全性产生新机会。"),
                _section("risk", "失败与风险", "耐药异质性、间质性肺病、心脏毒性和脑转移控制是常见风险维度。", "优先补充耐药后分层、联合治疗安全窗和真实世界依从性。", "高临床成熟度不代表所有新机制都已被验证。"),
            ],
            sources=[
                _source("uniprot-p00533", "EGFR · UniProt P00533", "UniProt", "https://www.uniprot.org/uniprotkb/P00533/entry", "UniProt data: CC BY 4.0"),
                _source("opentargets-egfr", "EGFR · Open Targets Platform", "Open Targets", "https://platform.opentargets.org/target/ENSG00000146648", "Open Targets platform licence applies"),
                _source("trials-egfr-nsclc", "EGFR NSCLC · ClinicalTrials.gov search", "U.S. National Library of Medicine", "https://clinicaltrials.gov/search?term=EGFR%20NSCLC", "ClinicalTrials.gov terms apply"),
            ],
            disclaimer="公开来源归一化示范快照；请以当前监管标签、注册试验和原始论文进行项目决策。",
        ),
    ]
    return [entry.model_copy(deep=True, update={"source_count": len(entry.sources)}) for entry in entries]


def public_library_summaries(*, updated_at: str | None = None) -> list[PublicLibrarySummary]:
    return [
        PublicLibrarySummary(
            slug=entry.slug,
            target=entry.target,
            headline=entry.headline,
            summary=entry.summary,
            updated_at=entry.updated_at,
            source_count=len(entry.sources),
            access_scope="public",
        )
        for entry in public_library_entries(updated_at=updated_at)
    ]


def get_public_library_entry(slug: str, *, updated_at: str | None = None) -> PublicLibraryEntry | None:
    normalized = slug.strip().lower()
    return next((entry for entry in public_library_entries(updated_at=updated_at) if entry.slug == normalized), None)
