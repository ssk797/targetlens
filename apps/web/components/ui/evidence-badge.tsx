import type { EvidenceLevel, SourceTier } from "@/lib/types/domain";

export function EvidenceBadge({ level }: { level: EvidenceLevel }) {
  return <span className={`evidence-badge evidence-${level.toLowerCase()}`}>{level}</span>;
}

export function SourceTierBadge({ tier }: { tier: SourceTier }) {
  return <span className="source-tier-badge">{tier}</span>;
}
