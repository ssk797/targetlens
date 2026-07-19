export type EvidenceLevel = "E1" | "E2" | "E3" | "E4" | "E5";
export type SourceTier = "T0" | "T1" | "T2" | "T3" | "T4";
export type RiskSeverity = "R1" | "R2" | "R3" | "R4";

export interface SourceRef {
  id: string;
  title: string;
  organization: string;
  url: string;
  tier: SourceTier;
  publishedAt?: string;
  retrievedAt: string;
  locator?: string;
}

export interface EvidenceItem {
  id: string;
  level: EvidenceLevel;
  polarity: "SUPPORTS" | "CONTRADICTS" | "NEUTRAL";
  statement: string;
  studyType: string;
  disease?: string;
  modelOrPopulation?: string;
  limitations: string[];
  source: SourceRef;
  reviewStatus: "AUTO_ACCEPTED" | "PENDING" | "REVIEWED";
}

export interface TargetIdentity {
  symbol: string;
  name: string;
  aliases: string[];
  uniprotId: string;
}

export interface ResearchScope {
  disease: string;
  modality: string;
  question: string;
}

export interface TargetMetrics {
  evidenceMaturity: string;
  highestClinicalStage: string;
  primaryModality: string;
  riskStatus: string;
  competition: string;
  citationCoverage: string;
}

export interface BiologySectionData {
  summary: string;
  mechanism: string[];
  functions: string[];
  disputes: string[];
}

export interface ExpressionSectionData {
  summary: string;
  tumorSignals: Array<{ label: string; level: "高" | "中" | "低" | "证据不足"; note: string }>;
  normalTissue: string[];
  population: string[];
}

export interface ModalityAssessment {
  modality: string;
  fit: "HIGH" | "MEDIUM" | "LOW" | "INSUFFICIENT";
  evidence: string;
  limitation: string;
  verify: string;
}

export interface DrugProgram {
  name: string;
  sponsor: string;
  modality: string;
  stage: string;
  status: string;
  note: string;
  sourceIds: string[];
}

export interface ClinicalTrial {
  identifier: string;
  title: string;
  phase: string;
  status: string;
  sourceId: string;
}

export interface RiskEvent {
  id: string;
  severity: RiskSeverity;
  type: string;
  title: string;
  scope: string;
  fact: string;
  impact: string;
  sourceId: string;
  review: string;
  mitigable: boolean;
}

export interface CompetitionSummary {
  summary: string;
  signals: string[];
  whitespace: string;
}

export interface KnowledgeGraphData {
  nodes: Array<{ id: string; label: string; type: string }>;
  edges: Array<{ source: string; target: string; relation: string; evidenceIds: string[] }>;
}

export interface TargetConclusion {
  verdict: string;
  boundaries: string[];
  unknowns: string[];
}

export interface ResearchWorkflowStep {
  id: string;
  label: string;
  status: "READY" | "PARTIAL" | "DEGRADED" | "PENDING";
  detail: string;
}

export interface CardMetadata {
  isMock: boolean;
  generatedForDemo: boolean;
  schemaVersion?: number;
  dataCutoff: string;
  disclaimer: string;
  workflow?: ResearchWorkflowStep[];
}

export interface TargetCard {
  id: string;
  sessionId: string;
  version: number;
  target: TargetIdentity;
  scope: ResearchScope;
  metrics: TargetMetrics;
  executiveSummary: string;
  biology: BiologySectionData;
  expression: ExpressionSectionData;
  validation: EvidenceItem[];
  druggability: ModalityAssessment[];
  drugs: DrugProgram[];
  trials: ClinicalTrial[];
  competition: CompetitionSummary;
  risks: RiskEvent[];
  graph: KnowledgeGraphData;
  conclusions: TargetConclusion;
  metadata: CardMetadata;
}

export interface GroundedClaim {
  id: string;
  statement: string;
  evidenceIds: string[];
  certainty: "HIGH" | "MEDIUM" | "LOW";
  limitations: string[];
}

export interface GroundedAnswer {
  id: string;
  status: "SUPPORTED" | "PARTIAL" | "INSUFFICIENT_EVIDENCE" | "CONFLICTING_EVIDENCE" | "REVIEW_REQUIRED";
  summary: string;
  claims: GroundedClaim[];
  conflicts: string[];
  nextActions: string[];
  dataCutoff: string;
  provider?: string;
  /** User-message id answered by this response; used for ordered replay. */
  replyTo?: string | null;
}

export interface DecisionOption {
  type: string;
  title: string;
  content: string;
  evidenceIds: string[];
  limitation: string;
  priority: "P0" | "P1" | "P2";
  cost: "低" | "中" | "高";
}

export interface DecisionMemo {
  /** The user question that explicitly requested this memo. */
  triggerQuestion?: string | null;
  createdAt?: string;
  projectDefinition: string;
  whyNow: string;
  hardParts: string[];
  options: DecisionOption[];
  nextValidation: string[];
  exitCriteria: string[];
  boundaries: string[];
  radar: ScoreDimension[];
  riskAlerts: string[];
}

export interface ScoreDimension {
  label: string;
  value: number;
  note: string;
}

export interface RedFlag {
  id: string;
  title: string;
  severity: RiskSeverity;
  sourceId: string;
  impact: string;
  mitigable: boolean;
}

export interface ScoreSnapshot {
  baseOpportunity: number;
  riskBurden: number;
  evidenceConfidence: number;
  adjustedDirectionIndex: number;
  recommendation: "STRONG_GO" | "GO" | "CONDITIONAL_GO" | "WATCH" | "NO_GO";
  dimensions: ScoreDimension[];
  redFlags: RedFlag[];
  ruleVersion: string;
}

export interface ResearchSession {
  id: string;
  title: string;
  subtitle: string;
  status: "READY" | "PROCESSING" | "UPDATED" | "DRAFT";
  updatedAt: string;
  pinned?: boolean;
}

export interface TutorialLesson {
  id: string;
  number: number;
  title: string;
  kind: "IDENTITY" | "READING" | "EVIDENCE" | "DECISION";
  duration: string;
  completed: boolean;
}

export interface TutorialCourse {
  id: string;
  title: string;
  target: string;
  description: string;
  lessons: TutorialLesson[];
}
