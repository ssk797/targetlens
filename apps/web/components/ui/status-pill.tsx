import type { ReactNode } from "react";

interface StatusPillProps {
  children: ReactNode;
  tone?: "blue" | "green" | "amber" | "red" | "slate";
  dot?: boolean;
}

export function StatusPill({ children, tone = "slate", dot = false }: StatusPillProps) {
  return (
    <span className={`status-pill status-pill-${tone}`}>
      {dot ? <span className="status-dot" aria-hidden="true" /> : null}
      {children}
    </span>
  );
}
