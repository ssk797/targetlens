import { Check, ChevronDown, Circle, Loader2, RotateCcw, WifiOff } from "lucide-react";
import { useState } from "react";
import type { ResearchStage } from "@/components/workspace/workspace-shell";

const stageLabels: Array<{ id: ResearchStage; label: string; detail: string }> = [
  { id: "RESOLVING_ENTITY", label: "识别标准靶点", detail: "ROR1 · Q01973" },
  { id: "FETCHING_STRUCTURED_DATA", label: "读取疾病与表达证据", detail: "Open Targets · UniProt" },
  { id: "RETRIEVING_LITERATURE", label: "整理研究与临床来源", detail: "PubMed · ClinicalTrials.gov" },
  { id: "BUILDING_GRAPH", label: "建立关系与风险索引", detail: "1–2 跳关系" },
  { id: "GENERATING_CARD", label: "生成结构化靶点卡", detail: "证据绑定中" },
  { id: "READY", label: "研究卡已就绪", detail: "可继续追问" },
];

export function ResearchProgress({ stage, onRetry }: { stage: ResearchStage; onRetry?: () => void }) {
  const [expanded, setExpanded] = useState(false);
  const currentIndex = stageLabels.findIndex((item) => item.id === stage);

  return (
    <section className="progress-card" aria-label="研究进度" aria-live="polite">
      <div className="progress-card-head">
        <div className="progress-orb"><span /><span /><span /></div>
        <div><p className="eyebrow">Research trace · Mock</p><h3>{stage === "READY" ? "研究卡已生成" : "正在整理靶点研究"}</h3><p className="muted-copy">保留每一个证据来源，外部来源不可用时不会补造事实。</p></div>
        <button className="text-button" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>{expanded ? "收起来源状态" : "查看来源状态"}<ChevronDown size={15} className={expanded ? "rotate-180" : ""} /></button>
      </div>
      <div className="progress-steps">
        {stageLabels.map((item, index) => {
          const complete = index < currentIndex || stage === "READY";
          const current = item.id === stage;
          return <div className={`progress-step ${complete ? "progress-step-complete" : ""} ${current ? "progress-step-current" : ""}`} key={item.id}>
            <span className="progress-step-icon">{complete ? <Check size={14} /> : current ? <Loader2 size={14} className="spin" /> : <Circle size={10} />}</span>
            <span><strong>{item.label}</strong><small>{item.detail}</small></span>
          </div>;
        })}
      </div>
      {expanded ? <div className="source-status-row"><span><span className="source-online" /> 4 个来源正常</span><span><WifiOff size={14} /> 1 个来源待重试</span>{onRetry ? <button className="text-button" onClick={onRetry}><RotateCcw size={14} />重试失败来源</button> : null}</div> : null}
    </section>
  );
}
