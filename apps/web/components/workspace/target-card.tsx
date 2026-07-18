"use client";

import { ArrowDownRight, ArrowUpRight, ChevronDown, CircleDot, ExternalLink, FlaskConical, Info, ShieldAlert } from "lucide-react";
import type { EvidenceItem, TargetCard as TargetCardData } from "@/lib/types/domain";
import { EvidenceBadge, SourceTierBadge } from "@/components/ui/evidence-badge";
import { StatusPill } from "@/components/ui/status-pill";

interface TargetCardProps {
  card: TargetCardData;
  onEvidence: (evidence: EvidenceItem) => void;
  onExport: () => void;
  onRefresh?: () => void;
  officialOnly?: boolean;
  onToggleOfficial?: () => void;
}

export function TargetCard({ card, onEvidence, onExport, onRefresh, officialOnly = false, onToggleOfficial }: TargetCardProps) {
  const evidenceById = new Map(card.validation.map((item) => [item.id, item]));
  const firstEvidence = card.validation[0];
  const lastEvidence = card.validation[card.validation.length - 1];
  const openFirstEvidence = () => { if (firstEvidence) onEvidence(firstEvidence); };
  const openLastEvidence = () => { if (lastEvidence) onEvidence(lastEvidence); };
  const statusTone = card.metadata.isMock ? "amber" : "green";
  const workflow = card.metadata.workflow ?? [];

  return (
    <article className="target-card">
      <header className="target-card-header">
        <div className="target-card-title-row">
          <div className="target-symbol">{card.target.symbol.slice(0, 2)}</div>
          <div>
            <div className="target-title-line"><h2>{card.target.symbol}</h2><StatusPill tone={statusTone} dot>{card.metadata.isMock ? "离线缓存" : "实时来源"}</StatusPill><span className="version-label">卡片 V{card.version}</span></div>
            <p className="target-full-name">{card.target.name}</p>
            <p className="scope-line">当前范围：<strong>{card.scope.disease}</strong><span>·</span><strong>{card.scope.modality}</strong><span>·</span>{card.metadata.dataCutoff} 数据截至</p>
          </div>
        </div>
      <div className="target-header-actions"><button className="header-action" onClick={onRefresh}><ArrowDownRight size={15} />刷新</button><button className={`header-action ${officialOnly ? "header-action-active" : ""}`} onClick={onToggleOfficial} aria-pressed={officialOnly}><ShieldAlert size={15} />{officialOnly ? "仅官方 · 开" : "仅官方"}</button><button className="header-action" onClick={onExport}><ExternalLink size={15} />导出</button><button className="icon-button" aria-label="更多操作"><Info size={16} /></button></div>
      </header>

      <div className="metrics-strip">
        <Metric label="证据成熟度" value={card.metrics.evidenceMaturity} tone="blue" />
        <Metric label="最高临床阶段" value={card.metrics.highestClinicalStage} />
        <Metric label="主要药物形式" value={card.metrics.primaryModality} tone="blue" />
        <Metric label="风险状态" value={card.metrics.riskStatus} tone="amber" />
        <Metric label="竞争拥挤度" value={card.metrics.competition} />
        <Metric label="引用覆盖率" value={card.metrics.citationCoverage} tone="green" />
      </div>

      <div className="target-card-body">
        <section className="executive-summary">
          <div className="summary-marker"><CircleDot size={18} /></div>
          <div><p className="eyebrow">研究摘要</p><h3>{card.conclusions.verdict.split("。")[0]}</h3><p>{card.executiveSummary}</p></div>
          <StatusPill tone={card.metadata.isMock ? "amber" : "blue"}>{card.metadata.isMock ? "离线复核" : "待人工复核"}</StatusPill>
        </section>

        {workflow.length > 0 ? <section className="workflow-rail" aria-label="本次检索步骤"><div className="workflow-rail-head"><span className="mini-label">本次检索路径</span><span>按实体、来源、文献到证据逐步整合</span></div><div className="workflow-steps">{workflow.map((step, index) => <div className={`workflow-step workflow-${step.status.toLowerCase()}`} key={step.id}><span className="workflow-index">{String(index + 1).padStart(2, "0")}</span><div><strong>{step.label}</strong><small>{step.detail}</small></div></div>)}</div></section> : null}

        <div className="target-sections">
          <EvidenceSection number="01" title="生物学功能" summary={card.biology.summary} evidenceCount={Math.min(2, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="mechanism-chain" aria-label="机制链">
              {card.biology.mechanism.map((item, index) => <div className="mechanism-node" key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong>{index < card.biology.mechanism.length - 1 ? <ArrowRightSmall /> : null}</div>)}
            </div>
            <div className="split-content"><div><p className="mini-label">核心功能</p><ul className="compact-list">{card.biology.functions.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul></div><div><p className="mini-label">争议与边界</p><ul className="compact-list muted-list">{card.biology.disputes.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul></div></div>
          </EvidenceSection>

          <EvidenceSection number="02" title="表达与人群" summary={card.expression.summary} evidenceCount={Math.min(2, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="expression-grid">{card.expression.tumorSignals.map((signal) => <div className="expression-row" key={signal.label}><span className="expression-name">{signal.label}</span><span className={`level-bar level-${signal.level === "高" ? "high" : signal.level === "中" ? "medium" : signal.level === "低" ? "low" : "unknown"}`}><i /></span><strong>{signal.level}</strong><small>{signal.note}</small></div>)}</div>
            <div className="split-content"><div><p className="mini-label">正常组织暴露</p><ul className="compact-list">{card.expression.normalTissue.map((item) => <li key={item}>{item}</li>)}</ul></div><div><p className="mini-label">患者亚群提示</p><ul className="compact-list">{card.expression.population.map((item) => <li key={item}>{item}</li>)}</ul></div></div>
          </EvidenceSection>

          <EvidenceSection number="03" title="靶点验证" summary="证据支持研究假设，但证据强度和适用范围需要分开阅读。" evidenceCount={card.validation.length} onEvidence={openFirstEvidence}>
            <div className="table-wrap"><table className="evidence-table"><caption className="sr-only">{card.target.symbol} 靶点验证证据矩阵</caption><thead><tr><th>等级</th><th>结论</th><th>方向</th><th>研究类型</th><th>来源</th><th>状态</th></tr></thead><tbody>{card.validation.slice(0, 5).map((item) => <tr key={item.id} onClick={() => onEvidence(item)} tabIndex={0} onKeyDown={(event) => { if (event.key === "Enter") onEvidence(item); }}><td><EvidenceBadge level={item.level} /></td><td className="evidence-statement">{item.statement}</td><td><span className={`polarity polarity-${item.polarity.toLowerCase()}`}>{item.polarity === "SUPPORTS" ? "支持" : item.polarity === "CONTRADICTS" ? "限制" : "中性"}</span></td><td>{item.studyType}</td><td><SourceTierBadge tier={item.source.tier} /></td><td>{item.reviewStatus === "REVIEWED" ? "已复核" : "待复核"}</td></tr>)}</tbody></table></div>
          </EvidenceSection>

          <EvidenceSection number="04" title="成药逻辑" summary={`${card.scope.modality} 的形式适配需要独立验证，不能把靶点关联自动当成开发答案。`} evidenceCount={Math.min(2, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="table-wrap"><table className="modality-table"><caption className="sr-only">药物形式比较</caption><thead><tr><th>形式</th><th>适配</th><th>支持证据</th><th>主要限制</th><th>必须验证</th></tr></thead><tbody>{card.druggability.map((item) => <tr key={item.modality}><td><strong>{item.modality}</strong></td><td><span className={`fit-label fit-${item.fit.toLowerCase()}`}>{item.fit}</span></td><td>{item.evidence}</td><td>{item.limitation}</td><td>{item.verify}</td></tr>)}</tbody></table></div>
          </EvidenceSection>

          <EvidenceSection number="05" title="代表药物与临床" summary="登记信息用于确认项目和阶段，不能单独替代疗效判断。" evidenceCount={Math.min(card.drugs.length + card.trials.length, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="program-grid">{card.drugs.map((drug) => <div className="program-row" key={drug.name}><div className="program-icon"><FlaskConical size={17} /></div><div className="program-main"><strong>{drug.name}</strong><span>{drug.sponsor} · {drug.modality}</span></div><span className="program-stage">{drug.stage}</span><span className="program-status">{drug.status}</span></div>)}</div>
            <div className="trial-strip">{card.trials.map((trial) => <button key={trial.identifier} className="trial-chip" onClick={() => { const evidence = evidenceById.get(trial.sourceId) ?? firstEvidence; if (evidence) onEvidence(evidence); }}><span>{trial.identifier}</span><small>{trial.phase} · {trial.status}</small><ExternalLink size={13} /></button>)}</div>
          </EvidenceSection>

          <EvidenceSection number="06" title="竞争空间" summary={card.competition.summary} evidenceCount={Math.min(1, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="competition-layout"><div className="competition-signals">{card.competition.signals.map((signal, index) => <div className="competition-signal" key={signal}><span>0{index + 1}</span><strong>{signal}</strong><ArrowUpRight size={15} /></div>)}</div><div className="whitespace-note"><p className="mini-label">可探索空白</p><p>{card.competition.whitespace}</p></div></div>
          </EvidenceSection>

          <EvidenceSection number="07" title="风险审查" summary="风险红线单独展示，优先于总分，不把行业新闻直接当监管结论。" evidenceCount={card.risks.length} onEvidence={openLastEvidence}>
            <div className="risk-list">{card.risks.map((risk) => <button className="risk-row" key={risk.id} onClick={() => { const evidence = evidenceById.get(risk.sourceId) ?? lastEvidence; if (evidence) onEvidence(evidence); }}><span className={`risk-severity risk-${risk.severity.toLowerCase()}`}>{risk.severity}</span><span className="risk-type">{risk.type}</span><span className="risk-main"><strong>{risk.title}</strong><small>{risk.fact}</small></span><span className="risk-impact">{risk.impact}</span><ArrowUpRight size={15} /></button>)}</div>
          </EvidenceSection>

          <EvidenceSection number="08" title="结论与未知项" summary={card.conclusions.verdict} evidenceCount={card.conclusions.unknowns.length} onEvidence={openLastEvidence}>
            <div className="conclusion-grid"><div className="conclusion-verdict"><span className="verdict-arrow"><ArrowUpRight size={16} /></span><p>{card.conclusions.verdict}</p></div><div><p className="mini-label">结论边界</p><ul className="compact-list muted-list">{card.conclusions.boundaries.map((item) => <li key={item}>{item}</li>)}</ul></div><div><p className="mini-label">待回答问题</p><ul className="compact-list">{card.conclusions.unknowns.map((item) => <li key={item}>{item}</li>)}</ul></div></div>
          </EvidenceSection>
        </div>
      </div>
    </article>
  );
}

function Metric({ label, value, tone = "default" }: { label: string; value: string; tone?: "default" | "blue" | "amber" | "green" }) {
  return <div className="metric"><span>{label}</span><strong className={`metric-value metric-${tone}`}>{value}</strong></div>;
}

function EvidenceSection({ number, title, summary, evidenceCount, onEvidence, children }: { number: string; title: string; summary: string; evidenceCount: number; onEvidence: () => void; children: React.ReactNode }) {
  return <details className="evidence-section" open><summary><span className="section-number">{number}</span><span className="section-title-wrap"><strong>{title}</strong><small>{summary}</small></span><span className="section-evidence-count">{evidenceCount} 条证据</span><ChevronDown className="section-chevron" size={17} /></summary><div className="evidence-section-body"><div className="evidence-section-actions"><button className="source-inline-button" onClick={onEvidence}>查看支持来源 <ArrowUpRight size={14} /></button></div>{children}</div></details>;
}

function ArrowRightSmall() {
  return <span className="mechanism-arrow" aria-hidden="true">→</span>;
}
