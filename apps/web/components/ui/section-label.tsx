import type { ReactNode } from "react";

interface SectionLabelProps {
  eyebrow: string;
  title: string;
  note?: string;
  action?: ReactNode;
}

export function SectionLabel({ eyebrow, title, note, action }: SectionLabelProps) {
  return (
    <div className="section-label">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        {note ? <p className="section-note">{note}</p> : null}
      </div>
      {action ? <div className="section-action">{action}</div> : null}
    </div>
  );
}
