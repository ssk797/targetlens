"use client";

import { ArrowUpRight, BookOpen, CheckCircle2, Clock3, X } from "lucide-react";
import type { EvidenceItem } from "@/lib/types/domain";
import { EvidenceBadge, SourceTierBadge } from "@/components/ui/evidence-badge";

interface EvidenceDrawerProps {
  evidence: EvidenceItem | null;
  onClose: () => void;
}

export function EvidenceDrawer({ evidence, onClose }: EvidenceDrawerProps) {
  if (!evidence) return null;

  return (
    <aside className="evidence-drawer" role="dialog" aria-modal="true" aria-labelledby="evidence-title">
      <div className="drawer-header">
        <div>
          <p className="eyebrow">Evidence drawer</p>
          <h2 id="evidence-title">来源与证据</h2>
        </div>
        <button className="icon-button" onClick={onClose} aria-label="关闭证据抽屉">
          <X size={18} />
        </button>
      </div>

      <div className="drawer-content">
        <div className="drawer-source-hero">
          <div className="source-mark"><BookOpen size={18} /></div>
          <div>
            <p className="source-organization">{evidence.source.organization}</p>
            <h3>{evidence.source.title}</h3>
          </div>
        </div>

        <div className="drawer-badges">
          <EvidenceBadge level={evidence.level} />
          <SourceTierBadge tier={evidence.source.tier} />
          <span className="polarity-text">{evidence.polarity === "SUPPORTS" ? "支持" : evidence.polarity === "CONTRADICTS" ? "限制 / 反证" : "中性"}</span>
        </div>

        <section className="drawer-section">
          <p className="eyebrow">抽取结论</p>
          <p className="drawer-statement">{evidence.statement}</p>
        </section>

        <section className="drawer-section drawer-meta-grid">
          <div>
            <span>研究类型</span>
            <strong>{evidence.studyType}</strong>
          </div>
          <div>
            <span>研究范围</span>
            <strong>{evidence.disease ?? "跨癌种 / 通用"}</strong>
          </div>
          <div>
            <span>模型或人群</span>
            <strong>{evidence.modelOrPopulation ?? "未注明"}</strong>
          </div>
          <div>
            <span>审核状态</span>
            <strong className="inline-status"><CheckCircle2 size={14} />{evidence.reviewStatus === "REVIEWED" ? "已复核" : "待复核"}</strong>
          </div>
        </section>

        <section className="drawer-section">
          <div className="drawer-section-title"><p className="eyebrow">边界与限制</p><span className="drawer-count">{evidence.limitations.length} 条</span></div>
          <ul className="limitation-list">
            {evidence.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}
          </ul>
        </section>

        <section className="drawer-section source-record">
          <div className="drawer-section-title"><p className="eyebrow">来源记录</p><Clock3 size={15} /></div>
          <dl>
            <div><dt>来源等级</dt><dd><SourceTierBadge tier={evidence.source.tier} /></dd></div>
            <div><dt>抓取时间</dt><dd>{evidence.source.retrievedAt}</dd></div>
            {evidence.source.publishedAt ? <div><dt>发布日期</dt><dd>{evidence.source.publishedAt}</dd></div> : null}
            <div><dt>定位信息</dt><dd>{evidence.source.locator ?? "来源首页"}</dd></div>
          </dl>
          <a className="source-link" href={evidence.source.url} target="_blank" rel="noreferrer">
            打开原始来源 <ArrowUpRight size={14} />
          </a>
        </section>
      </div>
    </aside>
  );
}
