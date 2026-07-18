import { ArrowRight, CheckCircle2, Flag, FlaskConical, ShieldCheck } from "lucide-react";
import type { DecisionMemo as DecisionMemoData } from "@/lib/types/domain";
import { StatusPill } from "@/components/ui/status-pill";

export function DecisionMemo({ memo, sourceMode = "实时规则" }: { memo: DecisionMemoData; sourceMode?: string }) {
  return (
    <section className="decision-memo">
      <div className="decision-head">
        <div className="decision-icon"><Flag size={18} /></div>
        <div>
          <p className="eyebrow">Decision memo · {sourceMode}</p>
          <h3>差异化立项建议</h3>
          <p>把“值得研究”翻译成可验证、可退出的下一步。</p>
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
