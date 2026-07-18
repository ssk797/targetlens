"use client";

import { ArrowUp, FileText, Flag, LockKeyhole, Paperclip, Sparkles } from "lucide-react";
import { useState } from "react";

interface ResearchComposerProps {
  onSubmit: (value: string) => void;
  onDecision: () => void;
  onExport: () => void;
  disabled?: boolean;
}

const quickPrompts = ["快速梳理靶点", "分析患者分层", "判断药物形式", "检查失败风险", "生成差异化建议"];

export function ResearchComposer({ onSubmit, onDecision, onExport, disabled = false }: ResearchComposerProps) {
  const [value, setValue] = useState("");
  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  };

  return (
    <div className="composer-shell">
      <div className="composer-quick-row" aria-label="快捷追问">
        {quickPrompts.map((prompt) => <button key={prompt} className="quick-chip" onClick={() => prompt.includes("建议") ? onDecision() : setValue(prompt)}>{prompt}</button>)}
      </div>
      <div className="composer-box">
        <textarea value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); submit(); } }} placeholder="继续追问当前靶点，或描述一个研究问题…" aria-label="继续追问当前靶点" rows={2} disabled={disabled} />
        <div className="composer-toolbar">
          <div className="composer-tools"><button className="composer-tool" aria-label="附加当前区块"><Paperclip size={15} />引用当前区块</button><button className="composer-tool" aria-label="仅使用官方来源"><LockKeyhole size={15} />仅官方来源</button><button className="composer-tool" aria-label="生成报告" onClick={onExport}><FileText size={15} />导出</button></div>
          <div className="composer-actions"><span className="composer-hint">Shift + Enter 换行</span><button className="send-button" onClick={submit} disabled={!value.trim() || disabled} aria-label="发送追问"><ArrowUp size={17} /></button></div>
        </div>
      </div>
      <p className="composer-disclaimer"><Flag size={12} /> Mock 演示数据 · 关键结论请回到来源核验 · 不是医疗或监管建议</p>
    </div>
  );
}
