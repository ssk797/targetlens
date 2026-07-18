import type {
  DecisionMemo,
  EvidenceItem,
  GroundedAnswer,
  ScoreSnapshot,
  SourceRef,
  TargetCard,
  TutorialCourse,
  ResearchSession,
} from "@/lib/types/domain";

export const mockMetadata = {
  isMock: true,
  generatedForDemo: true,
  dataCutoff: "2026-07-18",
  disclaimer: "演示数据，不用于真实研发判断",
};

export const mockSources: SourceRef[] = [
  {
    id: "src-open-targets",
    title: "Open Targets Platform · ROR1 target profile",
    organization: "Open Targets",
    url: "https://platform.opentargets.org/target/ENSG00000185483",
    tier: "T1",
    retrievedAt: "2026-07-18",
    locator: "Target–disease association overview",
  },
  {
    id: "src-uniprot",
    title: "ROR1_HUMAN · UniProt Q01973",
    organization: "UniProt",
    url: "https://www.uniprot.org/uniprotkb/Q01973/entry",
    tier: "T1",
    retrievedAt: "2026-07-18",
    locator: "Function and subcellular location",
  },
  {
    id: "src-pubmed-ror1",
    title: "ROR1 as a therapeutic target in cancer research",
    organization: "PubMed",
    url: "https://pubmed.ncbi.nlm.nih.gov/?term=ROR1+cancer+therapeutic+target",
    tier: "T2",
    publishedAt: "2024",
    retrievedAt: "2026-07-18",
    locator: "Review and translational evidence set",
  },
  {
    id: "src-clinicaltrials",
    title: "ClinicalTrials.gov · ROR1 intervention search",
    organization: "ClinicalTrials.gov",
    url: "https://clinicaltrials.gov/search?term=ROR1",
    tier: "T1",
    retrievedAt: "2026-07-18",
    locator: "Study registry and status fields",
  },
  {
    id: "src-chembl",
    title: "ChEMBL target and bioactivity records",
    organization: "ChEMBL",
    url: "https://www.ebi.ac.uk/chembl/explore/target/CHEMBL4523",
    tier: "T1",
    retrievedAt: "2026-07-18",
    locator: "Target and modality context",
  },
  {
    id: "src-review-note",
    title: "Demo review note · normal tissue window",
    organization: "TargetLens demo fixture",
    url: "https://example.org/targetlens/demo-review-note",
    tier: "T4",
    retrievedAt: "2026-07-18",
    locator: "Human review placeholder",
  },
];

export const mockEvidence: EvidenceItem[] = [
  {
    id: "ev-biology-01",
    level: "E2",
    polarity: "SUPPORTS",
    statement: "ROR1 是一种受体酪氨酸激酶样孤儿受体，在胚胎发育和部分肿瘤相关信号中被研究。",
    studyType: "结构化数据库与功能注释",
    modelOrPopulation: "跨癌种公共数据",
    limitations: ["功能注释不等于特定适应证中的因果验证。"],
    source: mockSources[1],
    reviewStatus: "REVIEWED",
  },
  {
    id: "ev-expression-01",
    level: "E3",
    polarity: "SUPPORTS",
    statement: "公开表达资料提示，ROR1 在部分肿瘤亚群中存在相对高表达或异常表达信号。",
    studyType: "转录组与表达整合",
    disease: "三阴性乳腺癌（演示范围）",
    modelOrPopulation: "公开队列的相对等级",
    limitations: ["本卡不展示未经核验的精确表达数值。", "队列、抗体和阈值差异可能改变结论。"],
    source: mockSources[0],
    reviewStatus: "PENDING",
  },
  {
    id: "ev-modality-01",
    level: "E3",
    polarity: "SUPPORTS",
    statement: "ADC 方向的工作假设来自细胞表面可及性、抗体递送和肿瘤选择性之间的组合逻辑。",
    studyType: "转化研究综述",
    disease: "实体瘤（演示范围）",
    modelOrPopulation: "体外与转化证据摘要",
    limitations: ["体外信号不能替代临床确证。", "毒性窗口仍需在目标适应证中单独验证。"],
    source: mockSources[2],
    reviewStatus: "PENDING",
  },
  {
    id: "ev-clinical-01",
    level: "E4",
    polarity: "NEUTRAL",
    statement: "临床注册信息可用于确认项目存在及试验状态，但不能单独证明疗效或商业成功。",
    studyType: "临床试验注册信息",
    disease: "多适应证",
    modelOrPopulation: "注册信息字段",
    limitations: ["登记状态与最终读出之间存在时间差。", "完成不等于成功。"],
    source: mockSources[3],
    reviewStatus: "REVIEWED",
  },
  {
    id: "ev-competition-01",
    level: "E4",
    polarity: "CONTRADICTS",
    statement: "竞争格局提示，ROR1 方向并非空白赛道，差异化需要落到患者选择、表位或临床策略。",
    studyType: "项目与管线检索",
    disease: "肿瘤适应证",
    modelOrPopulation: "公开项目记录",
    limitations: ["项目披露并不完整，竞争强度需要持续更新。"],
    source: mockSources[4],
    reviewStatus: "PENDING",
  },
  {
    id: "ev-window-01",
    level: "E5",
    polarity: "NEUTRAL",
    statement: "正常组织暴露窗口和可控性仍是本方向的关键未知项，必须通过专门实验设计验证。",
    studyType: "风险审查占位",
    disease: "当前研究范围",
    modelOrPopulation: "人工复核项",
    limitations: ["这是演示用待验证项，不代表监管结论。"],
    source: mockSources[5],
    reviewStatus: "PENDING",
  },
];

export const mockTargetCard: TargetCard = {
  id: "card-ror1-v1",
  sessionId: "session-ror1",
  version: 1,
  target: {
    symbol: "ROR1",
    name: "Receptor tyrosine kinase-like orphan receptor 1",
    aliases: ["NTRKR1", "ROR1 receptor"],
    uniprotId: "Q01973",
  },
  scope: {
    disease: "三阴性乳腺癌",
    modality: "ADC",
    question: "ROR1 在三阴性乳腺癌中是否适合开发 ADC？",
  },
  metrics: {
    evidenceMaturity: "中等 · E3",
    highestClinicalStage: "注册信息可见 · 需复核",
    primaryModality: "ADC 假设",
    riskStatus: "有待验证红线",
    competition: "中等偏拥挤",
    citationCoverage: "78% · 演示值",
  },
  executiveSummary:
    "ROR1 具备形成 ADC 研究假设的生物学与可及性线索，但目前更适合被定义为“有条件推进、先验证选择性窗口”的方向，而不是直接给出开发结论。",
  biology: {
    summary: "公开功能注释与转化研究共同支持 ROR1 作为肿瘤生物学研究对象，但特定适应证中的因果链仍需补强。",
    mechanism: ["发育相关调控", "ROR1 异常或再表达", "细胞迁移 / 存活信号", "肿瘤表型假设", "潜在抗体递送干预"],
    functions: ["受体样跨膜蛋白", "研究集中在肿瘤相关表达和信号", "表面可及性是 ADC 假设的必要前提"],
    disputes: ["不同队列的表达分布并不一致。", "表达强度与药物敏感性之间不能直接画等号。"],
  },
  expression: {
    summary: "当前仅使用相对等级表达“研究信号”，不伪造精确生物学数值。",
    tumorSignals: [
      { label: "三阴性乳腺癌", level: "中", note: "存在研究信号，患者分层方式待定义" },
      { label: "血液肿瘤亚群", level: "高", note: "文献关注度较高，需避免跨适应证外推" },
      { label: "其他实体瘤", level: "证据不足", note: "需要先固定检测和阈值" },
    ],
    normalTissue: ["正常组织表达窗口：待专门验证", "脱靶暴露：不能由公开表达表单独推断", "安全性结论：当前不形成正式结论"],
    population: ["优先考虑可检测、可复现的 ROR1 阳性亚群", "将表达、内吞和 payload 敏感性分开验证", "避免把单一 IHC 阈值当作完整生物标志物"],
  },
  validation: mockEvidence,
  druggability: [
    { modality: "ADC", fit: "MEDIUM", evidence: "表面可及性与递送逻辑支持进一步研究", limitation: "正常组织窗口和内吞差异未知", verify: "配对表达、内吞、payload 敏感性实验" },
    { modality: "双抗", fit: "MEDIUM", evidence: "可通过组合选择性构建差异化假设", limitation: "机制与安全窗口需要重新建模", verify: "双靶点表达与功能联动验证" },
    { modality: "单抗", fit: "LOW", evidence: "可作为结合和分层工具", limitation: "单抗本身的效应路径不够清晰", verify: "结合、内吞和功能阻断对照" },
    { modality: "小分子", fit: "INSUFFICIENT", evidence: "当前公开资料不足以支持优先级", limitation: "缺少明确可成药口袋和选择性依据", verify: "结构与药化可行性评估" },
  ],
  drugs: [
    { name: "ROR1-ADC 项目 A（演示）", sponsor: "公开项目记录", modality: "ADC", stage: "临床探索", status: "状态需复核", note: "仅展示项目结构，不代表疗效判断", sourceIds: ["ev-clinical-01"] },
    { name: "ROR1 双抗项目 B（演示）", sponsor: "公开项目记录", modality: "双抗", stage: "临床前 / 早期", status: "公开信息有限", note: "用于比较差异化路径", sourceIds: ["ev-competition-01"] },
    { name: "ROR1 结合工具 C（演示）", sponsor: "研究工具记录", modality: "抗体工具", stage: "研究工具", status: "非治疗项目", note: "用于实验设计与检测上下文", sourceIds: ["ev-biology-01"] },
  ],
  trials: [
    { identifier: "NCT-DEMO-ROR1", title: "ROR1 相关干预的注册信息入口（演示）", phase: "早期", status: "需复核", sourceId: "src-clinicaltrials" },
    { identifier: "REG-DEMO-02", title: "跨适应证项目记录汇总（演示）", phase: "探索", status: "公开字段不完整", sourceId: "src-clinicaltrials" },
  ],
  competition: {
    summary: "公开项目和研究热度表明方向并非空白，单纯“做 ROR1 ADC”不足以构成差异化。",
    signals: ["已有同靶点项目叙事", "患者选择策略仍有空间", "表位、内吞和 payload 组合需要对比"],
    whitespace: "优先寻找可验证的 ROR1 阳性人群与临床筛选策略，把差异化落到开发可执行性。",
  },
  risks: [
    { id: "risk-window", severity: "R3", type: "安全性", title: "正常组织窗口尚未锁定", scope: "当前适应证", fact: "公开表达与功能资料不能单独证明安全窗口。", impact: "建议等级受红线限制，需进入人工复核。", sourceId: "ev-window-01", review: "待人工复核", mitigable: true },
    { id: "risk-evidence", severity: "R2", type: "证据", title: "跨适应证外推风险", scope: "TNBC → 其他癌种", fact: "不同癌种的表达、内吞和 payload 敏感性可能不同。", impact: "不能用单一适应证证据支撑全部开发范围。", sourceId: "ev-expression-01", review: "部分复核", mitigable: true },
    { id: "risk-competition", severity: "R2", type: "竞争", title: "同靶点叙事拥挤", scope: "ADC / 双抗", fact: "公开项目和研究关注度提示竞争窗口有限。", impact: "必须将患者选择或临床策略作为差异化的一部分。", sourceId: "ev-competition-01", review: "待复核", mitigable: true },
  ],
  graph: {
    nodes: [
      { id: "ror1", label: "ROR1", type: "靶点" },
      { id: "tnbc", label: "三阴性乳腺癌", type: "疾病" },
      { id: "adc", label: "ADC", type: "药物形式" },
      { id: "expression", label: "表面表达", type: "证据概念" },
      { id: "window", label: "正常组织窗口", type: "风险" },
    ],
    edges: [
      { source: "ror1", target: "tnbc", relation: "研究关联", evidenceIds: ["ev-expression-01"] },
      { source: "ror1", target: "adc", relation: "药物形式假设", evidenceIds: ["ev-modality-01"] },
      { source: "ror1", target: "expression", relation: "依赖", evidenceIds: ["ev-biology-01", "ev-expression-01"] },
      { source: "adc", target: "window", relation: "受限于", evidenceIds: ["ev-window-01"] },
    ],
  },
  conclusions: {
    verdict: "条件性推进：先完成患者选择与正常组织窗口验证，再决定是否进入候选分子优化。",
    boundaries: ["当前为结构化研究假设，不是临床或监管结论。", "所有具体项目状态需回到原始来源复核。"],
    unknowns: ["可复现的 ROR1 阳性阈值", "正常组织窗口", "内吞与 payload 敏感性的耦合", "真实竞争项目的最新状态"],
  },
  metadata: mockMetadata,
};

export const mockAnswers: GroundedAnswer[] = [
  {
    id: "answer-1",
    status: "PARTIAL",
    summary: "目前更适合把 ROR1 ADC 定义为“有条件推进”的研究方向，而不是直接进入候选分子开发。",
    claims: [
      { id: "claim-1", statement: "表面可及性与转化研究为 ADC 假设提供了方向性支持。", evidenceIds: ["ev-biology-01", "ev-modality-01"], certainty: "MEDIUM", limitations: ["尚未形成当前适应证中的临床确证。"] },
      { id: "claim-2", statement: "正常组织窗口是决定能否推进的关键门槛。", evidenceIds: ["ev-window-01"], certainty: "HIGH", limitations: ["需要专门实验而非继续外推公开表达。"] },
    ],
    conflicts: ["表达信号与疗效预测之间存在证据缺口。"],
    nextActions: ["先定义阳性患者检测方案", "补齐正常组织窗口实验", "对比表位与 payload 组合"],
    dataCutoff: "2026-07-18",
  },
  {
    id: "answer-2",
    status: "SUPPORTED",
    summary: "最值得优先验证的是“可检测的人群 + 可解释的内吞/效应关系”，而不是扩展更多癌种。",
    claims: [
      { id: "claim-3", statement: "患者分层和检测可复现性决定研发假设能否被临床执行。", evidenceIds: ["ev-expression-01", "ev-modality-01"], certainty: "MEDIUM", limitations: ["需要用同一检测体系进行跨样本验证。"] },
    ],
    conflicts: [],
    nextActions: ["建立 IHC / RNA / 蛋白表面表达的对照矩阵", "把内吞作为独立验证终点"],
    dataCutoff: "2026-07-18",
  },
  {
    id: "answer-3",
    status: "CONFLICTING_EVIDENCE",
    summary: "公开项目数量和登记状态可以证明竞争存在，但不足以证明竞争者已经建立临床优势。",
    claims: [
      { id: "claim-4", statement: "ROR1 方向需要用患者选择和临床策略形成差异化。", evidenceIds: ["ev-competition-01", "ev-clinical-01"], certainty: "MEDIUM", limitations: ["公开项目披露有时间差和不完整性。"] },
    ],
    conflicts: ["项目存在 ≠ 项目成功；注册状态 ≠ 疗效结论。"],
    nextActions: ["按适应证、表位和阶段拆分竞争地图", "为每个竞争判断保留原始来源"],
    dataCutoff: "2026-07-18",
  },
];

export const mockDecisionMemo: DecisionMemo = {
  projectDefinition: "在可复现的 ROR1 阳性三阴性乳腺癌人群中，评估具有明确内吞和安全窗口假设的 ADC 方案。",
  whyNow: "已有生物学线索、公开项目和检测工具可以支撑快速验证，但证据尚未闭环，适合先做小范围决策验证。",
  hardParts: ["证明目标患者而非泛肿瘤表达", "把表面表达、内吞和 payload 敏感性连成可测试链条", "在竞争存在时形成临床可执行差异化"],
  options: [
    { type: "BIOMARKER", title: "以可复现分层作为第一差异化", content: "先定义检测组合与阳性阈值，再选择最有可能产生效应的患者亚群。", evidenceIds: ["ev-expression-01"], limitation: "检测阈值可能在不同平台上漂移。", priority: "P0", cost: "中" },
    { type: "EPITOPE_OR_BINDING_SITE", title: "围绕表位与内吞效率做筛选", content: "把结合位置、内吞速度和 payload 暴露作为候选分子筛选的组合终点。", evidenceIds: ["ev-modality-01"], limitation: "需要建立可复现的细胞和组织模型。", priority: "P0", cost: "高" },
    { type: "CLINICAL_STRATEGY", title: "先窄适应证、再扩展", content: "围绕可检测人群设计早期临床验证，避免用宽泛癌种叙事掩盖证据缺口。", evidenceIds: ["ev-clinical-01", "ev-competition-01"], limitation: "入组速度和市场空间需要单独评估。", priority: "P1", cost: "中" },
  ],
  nextValidation: ["确定 ROR1 阳性检测方案和跨平台一致性", "补充正常组织暴露与安全窗实验", "对 2–3 个表位 / payload 组合建立对照"],
  exitCriteria: ["无法形成稳定、可复现的患者分层", "正常组织窗口显示不可缓解风险", "候选分子在内吞和效应上不具备可解释优势"],
  boundaries: ["本建议只服务于研究优先级讨论，不替代药理、毒理、临床或监管决策。", "Mock 来源与项目状态必须在真实数据接入后重新核对。"],
};

export const mockScore: ScoreSnapshot = {
  baseOpportunity: 72,
  riskBurden: 58,
  evidenceConfidence: 64,
  adjustedDirectionIndex: 52,
  recommendation: "CONDITIONAL_GO",
  dimensions: [
    { label: "临床需求", value: 70, note: "适应证仍需聚焦" },
    { label: "生物学验证", value: 68, note: "有线索、缺因果闭环" },
    { label: "患者分层", value: 54, note: "检测方案待定义" },
    { label: "成药性", value: 66, note: "ADC 逻辑可研究" },
    { label: "竞争空间", value: 48, note: "同靶点叙事较多" },
    { label: "临床可行性", value: 51, note: "需要验证入组路径" },
    { label: "安全可控性", value: 42, note: "窗口是首要门槛" },
  ],
  redFlags: [
    { id: "flag-window", title: "正常组织窗口未锁定", severity: "R3", sourceId: "ev-window-01", impact: "当前建议等级受红线限制", mitigable: true },
  ],
  ruleVersion: "demo-rules-0.1",
};

export const mockSessions: ResearchSession[] = [
  { id: "session-ror1", title: "ROR1 · ADC 立项判断", subtitle: "三阴性乳腺癌 · 最近更新", status: "READY", updatedAt: "今天 14:32", pinned: true },
  { id: "session-ccr8", title: "CCR8 · 免疫微环境", subtitle: "实体瘤 · 需要更新", status: "UPDATED", updatedAt: "昨天 18:10" },
  { id: "session-egfr", title: "EGFR · 教程练习", subtitle: "证据分级 · 草稿", status: "DRAFT", updatedAt: "7 月 15 日" },
];

export const mockTutorial: TutorialCourse = {
  id: "course-egfr",
  title: "EGFR 靶点研读基础",
  target: "EGFR",
  description: "用九个关卡练习从靶点身份、证据强度到立项判断的完整方法。",
  lessons: [
    { id: "lesson-1", number: 1, title: "靶点身份：先确认你研究的对象", kind: "IDENTITY", duration: "6 分钟", completed: false },
    { id: "lesson-2", number: 2, title: "别名和实体：避免把药物当靶点", kind: "IDENTITY", duration: "7 分钟", completed: false },
    { id: "lesson-3", number: 3, title: "从功能注释到研究假设", kind: "READING", duration: "8 分钟", completed: false },
    { id: "lesson-4", number: 4, title: "证据分级：体外不等于临床确证", kind: "EVIDENCE", duration: "10 分钟", completed: false },
    { id: "lesson-5", number: 5, title: "读懂冲突证据", kind: "EVIDENCE", duration: "8 分钟", completed: false },
    { id: "lesson-6", number: 6, title: "表达、依赖与患者分层", kind: "READING", duration: "9 分钟", completed: false },
    { id: "lesson-7", number: 7, title: "成药形式比较", kind: "DECISION", duration: "9 分钟", completed: false },
    { id: "lesson-8", number: 8, title: "风险红线和退出条件", kind: "DECISION", duration: "8 分钟", completed: false },
    { id: "lesson-9", number: 9, title: "写出一页立项判断", kind: "DECISION", duration: "12 分钟", completed: false },
  ],
};
