"use client";

import { ArrowDownRight, ArrowUpRight, ChevronDown, CircleDot, ExternalLink, FlaskConical, Info, ShieldAlert } from "lucide-react";
import { useState } from "react";
import type { EvidenceItem, TargetCard as TargetCardData } from "@/lib/types/domain";
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
  const [infoOpen, setInfoOpen] = useState(false);
  const evidenceById = new Map(card.validation.map((item) => [item.id, item]));
  const firstEvidence = card.validation[0];
  const lastEvidence = card.validation[card.validation.length - 1];
  const openFirstEvidence = () => { if (firstEvidence) onEvidence(firstEvidence); };
  const openLastEvidence = () => { if (lastEvidence) onEvidence(lastEvidence); };
  const statusTone = card.metadata.isMock ? "amber" : "green";
  const workflow = card.metadata.workflow ?? [];
  const uniqueFunctions = Array.from(new Set(card.biology.functions));
  const uniqueMechanism = Array.from(new Set(card.biology.mechanism));

  return (
    <article className="target-card">
      <header className="target-card-header">
        <div className="target-card-title-row">
          <div className="target-symbol">{card.target.symbol.slice(0, 2)}</div>
          <div>
            <div className="target-title-line"><h2>{card.target.symbol}</h2><StatusPill tone={statusTone} dot>{card.metadata.isMock ? "离线缓存" : "实时来源"}</StatusPill><span className="version-label">卡片 V{card.version}</span></div>
            <p className="target-full-name">{card.target.name}</p>
            <p className="scope-line">当前范围：<strong>{card.scope.disease}</strong><span>·</span><strong>{card.scope.modality}</strong><span>·</span>{card.metadata.dataCutoff} 数据截至</p>
            <p className="scope-question"><span>研究问题</span>{card.scope.question}</p>
          </div>
        </div>
      <div className="target-header-actions"><button className="header-action" onClick={onRefresh}><ArrowDownRight size={15} />刷新</button><button className={`header-action ${officialOnly ? "header-action-active" : ""}`} onClick={onToggleOfficial} aria-pressed={officialOnly}><ShieldAlert size={15} />{officialOnly ? "仅官方 · 开" : "仅官方"}</button><button className="header-action" onClick={onExport}><ExternalLink size={15} />导出</button><div className="card-info-wrap"><button className="icon-button" aria-label="卡片说明" aria-expanded={infoOpen} onClick={() => setInfoOpen((value) => !value)}><Info size={16} /></button>{infoOpen ? <div className="card-info-popover" role="dialog" aria-label="卡片说明"><p className="eyebrow">卡片说明</p><h4>证据整合结果</h4><p>这张卡按当前问题实时归一化靶点、来源与证据。内部知识图谱只用于关联检索，不会作为前台结论单独展示。</p><dl><div><dt>数据截至</dt><dd>{card.metadata.dataCutoff}</dd></div><div><dt>来源状态</dt><dd>{card.metadata.isMock ? "离线缓存，需复核" : "实时来源，需人工复核"}</dd></div></dl><button className="text-button" onClick={() => setInfoOpen(false)}>知道了</button></div> : null}</div></div>
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
              {uniqueMechanism.map((item, index) => <div className="mechanism-node" key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong>{index < uniqueMechanism.length - 1 ? <ArrowRightSmall /> : null}</div>)}
            </div>
            <div className="split-content"><div><p className="mini-label">核心功能</p><ul className="compact-list">{uniqueFunctions.map((item) => <li key={item}>{item}</li>)}</ul></div><div><p className="mini-label">争议与边界</p><ul className="compact-list muted-list">{card.biology.disputes.map((item) => <li key={item}>{item}</li>)}</ul></div></div>
          </EvidenceSection>

          <EvidenceSection number="02" title="肿瘤表达" summary={card.expression.summary} evidenceCount={Math.min(2, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="expression-grid">{card.expression.tumorSignals.map((signal) => <div className="expression-row" key={signal.label}><span className="expression-name">{signal.label}</span><span className={`level-bar level-${signal.level === "高" ? "high" : signal.level === "中" ? "medium" : signal.level === "低" ? "low" : "unknown"}`}><i /></span><strong>{signal.level}</strong><small>{signal.note}</small></div>)}</div>
            <div className="split-content"><div><p className="mini-label">正常组织暴露</p><ul className="compact-list">{card.expression.normalTissue.map((item) => <li key={item}>{item}</li>)}</ul></div><div><p className="mini-label">患者亚群提示</p><ul className="compact-list">{card.expression.population.map((item) => <li key={item}>{item}</li>)}</ul></div></div>
          </EvidenceSection>

          <EvidenceSection number="03" title="成药逻辑" summary={`${card.scope.modality} 的形式适配需要独立验证，不能把靶点关联自动当成开发答案。`} evidenceCount={Math.min(2, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="table-wrap"><table className="modality-table"><caption className="sr-only">药物形式比较</caption><thead><tr><th>形式</th><th>适配</th><th>支持证据</th><th>主要限制</th><th>必须验证</th></tr></thead><tbody>{card.druggability.map((item) => <tr key={item.modality}><td><strong>{item.modality}</strong></td><td><span className={`fit-label fit-${item.fit.toLowerCase()}`}>{item.fit}</span></td><td>{item.evidence}</td><td>{item.limitation}</td><td>{item.verify}</td></tr>)}</tbody></table></div>
          </EvidenceSection>

          <EvidenceSection number="04" title="代表药物" summary={`${card.target.symbol} 当前归一化 ${card.drugs.length} 条项目/化合物线索，阶段与状态需回到来源复核。`} evidenceCount={Math.min(card.drugs.length, card.validation.length)} onEvidence={openFirstEvidence}>
            <div className="program-grid">{card.drugs.map((drug) => <div className="program-row" key={drug.name}><div className="program-icon"><FlaskConical size={17} /></div><div className="program-main"><strong>{drug.name}</strong><span>{drug.sponsor} · {drug.modality}</span></div><span className="program-stage">{drug.stage}</span><span className="program-status">{drug.status}</span></div>)}</div>
          </EvidenceSection>

          <EvidenceSection number="05" title="临床进展" summary={`${card.metrics.highestClinicalStage}；ClinicalTrials.gov 当前返回 ${card.trials.length} 条登记，企业/监管披露单独列在代表药物与证据中。`} evidenceCount={Math.min(card.trials.length, card.validation.length)} onEvidence={openFirstEvidence}>
            {card.trials.length > 0 ? <div className="trial-strip">{card.trials.map((trial) => <button key={trial.identifier} className="trial-chip" onClick={() => { const evidence = evidenceById.get(trial.sourceId) ?? firstEvidence; if (evidence) onEvidence(evidence); }}><span>{trial.identifier}</span><small>{trial.phase} · {trial.status}</small><ExternalLink size={13} /></button>)}</div> : <p className="empty-inline-state">ClinicalTrials.gov 本次未返回可归一化登记；若代表药物已有上市或企业披露，其状态来自单独的企业/监管来源，不与登记库命中混合。</p>}
          </EvidenceSection>

          <EvidenceSection number="06" title="失败风险" summary={`${card.target.symbol} 当前最需要复核的证据边界；来源命中不等于安全或疗效结论。`} evidenceCount={card.risks.length} onEvidence={openLastEvidence}>
            <div className="risk-list">{card.risks.map((risk) => <button className="risk-row" key={risk.id} onClick={() => { const evidence = evidenceById.get(risk.sourceId) ?? lastEvidence; if (evidence) onEvidence(evidence); }}><span className={`risk-severity risk-${risk.severity.toLowerCase()}`}>{risk.severity}</span><span className="risk-type">{risk.type}</span><span className="risk-main"><strong>{risk.title}</strong><small>{risk.fact}</small></span><span className="risk-impact">{risk.impact}</span><ArrowUpRight size={15} /></button>)}</div>
            {card.conclusions.unknowns.length > 0 ? <div className="risk-unknowns"><p className="mini-label">失败信号待验证</p><ul className="compact-list muted-list">{card.conclusions.unknowns.map((item) => <li key={item}>{item}</li>)}</ul></div> : null}
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
