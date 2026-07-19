import { ArrowRight, CheckCircle2, Flag, FlaskConical, ShieldCheck } from "lucide-react";
import type { DecisionMemo as DecisionMemoData, ScoreDimension } from "@/lib/types/domain";
import { StatusPill } from "@/components/ui/status-pill";

export function DecisionMemo({ memo, sourceMode = "实时规则" }: { memo: DecisionMemoData; sourceMode?: string }) {
  return (
    <section className="decision-memo">
      <div className="decision-head">
        <div className="decision-icon"><Flag size={18} /></div>
        <div>
          <p className="eyebrow">Decision memo · {sourceMode}</p>
          <h3>差异化立项建议</h3>
          <p>综合临床需求、靶点验证、竞争格局、近期风险预警与患者分层可执行性，给出可验证、可退出的下一步。</p>
        </div>
        <StatusPill tone="blue">P0 优先验证</StatusPill>
      </div>

      <div className="decision-definition">
        <span className="mini-label">项目定义</span>
        <p>{memo.projectDefinition}</p>
        <div className="decision-why">
          <span><FlaskConical size={15} />为什么现在</span>
          <p>{memo.whyNow}</p>
        </div>
      </div>

      <div className="decision-analysis-grid">
        <div className="decision-radar-panel">
          <div className="decision-subhead"><div><p className="mini-label">五维差异化雷达</p><span>分数越高代表当前证据下的相对优势越清晰</span></div><span className="radar-legend"><i />当前靶点</span></div>
          <RadarChart dimensions={memo.radar ?? []} />
        </div>
        <div className="decision-risk-panel">
          <div className="decision-subhead"><div><p className="mini-label">近期风险警示</p><span>来自本次检索的证据边界，不等同于监管结论</span></div></div>
          <ol className="risk-alert-list">{(memo.riskAlerts ?? []).slice(0, 5).map((item, index) => <li key={`${item}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{item}</p></li>)}</ol>
        </div>
      </div>

      <div className="decision-columns">
        <div>
          <p className="mini-label">难在哪里</p>
          <ul className="compact-list">{memo.hardParts.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
        <div>
          <p className="mini-label">差异化选项</p>
          <div className="decision-options">
            {memo.options.map((option) => (
              <div className="decision-option" key={option.title}>
                <div className="option-head"><span>{option.type}</span><strong>{option.priority}</strong></div>
                <h4>{option.title}</h4>
                <p>{option.content}</p>
                <div className="option-foot"><span>验证成本 · {option.cost}</span><span>{option.limitation}</span></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="decision-bottom-grid">
        <div>
          <p className="mini-label">下一步验证</p>
          <ul className="check-list">{memo.nextValidation.map((item) => <li key={item}><CheckCircle2 size={15} />{item}</li>)}</ul>
        </div>
        <div>
          <p className="mini-label">退出条件</p>
          <ul className="compact-list muted-list">{memo.exitCriteria.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      </div>

      <div className="decision-boundary"><ShieldCheck size={15} /><span>{memo.boundaries.join(" ")}</span><ArrowRight size={15} /></div>
    </section>
  );
}

function RadarChart({ dimensions }: { dimensions: ScoreDimension[] }) {
  const fallback: ScoreDimension[] = [
    { label: "临床需求", value: 0, note: "暂无评分" },
    { label: "靶点验证", value: 0, note: "暂无评分" },
    { label: "竞争格局", value: 0, note: "暂无评分" },
    { label: "风险可控性（近期预警反向）", value: 0, note: "暂无评分" },
    { label: "患者分层可执行性", value: 0, note: "暂无评分" },
  ];
  const axes = (dimensions.length === 5 ? dimensions : fallback).slice(0, 5);
  const width = 360;
  const height = 270;
  const center = { x: 180, y: 136 };
  const radius = 84;
  const angle = (index: number) => -Math.PI / 2 + (index * Math.PI * 2) / axes.length;
  const point = (index: number, scale: number) => ({ x: center.x + Math.cos(angle(index)) * radius * scale, y: center.y + Math.sin(angle(index)) * radius * scale });
  const polygon = (scale: number) => axes.map((_, index) => { const item = point(index, scale); return `${item.x},${item.y}`; }).join(" ");
  const valuePolygon = axes.map((item, index) => { const pointAtValue = point(index, Math.max(0, Math.min(100, item.value)) / 100); return `${pointAtValue.x},${pointAtValue.y}`; }).join(" ");

  return <svg className="radar-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="五维差异化雷达图"><title>五维差异化雷达图</title>{[0.25, 0.5, 0.75, 1].map((scale) => <polygon key={scale} points={polygon(scale)} className="radar-grid" />)}{axes.map((item, index) => { const end = point(index, 1); const label = point(index, 1.23); return <g key={item.label}><line x1={center.x} y1={center.y} x2={end.x} y2={end.y} className="radar-axis" /><text x={label.x} y={label.y} className="radar-label" textAnchor={label.x < center.x - 10 ? "end" : label.x > center.x + 10 ? "start" : "middle"} dominantBaseline={label.y < center.y ? "auto" : "hanging"}>{item.label}</text><text x={label.x} y={label.y + (label.y < center.y ? 14 : -14)} className="radar-value" textAnchor={label.x < center.x - 10 ? "end" : label.x > center.x + 10 ? "start" : "middle"}>{item.value}</text></g>; })}<polygon points={valuePolygon} className="radar-value-area" /><polyline points={`${valuePolygon} ${valuePolygon.split(" ")[0]}`} className="radar-value-line" />{axes.map((item, index) => { const dot = point(index, Math.max(0, Math.min(100, item.value)) / 100); return <circle key={`${item.label}-dot`} cx={dot.x} cy={dot.y} r="3.5" className="radar-dot"><title>{`${item.label}：${item.value} · ${item.note}`}</title></circle>; })}</svg>;
}
