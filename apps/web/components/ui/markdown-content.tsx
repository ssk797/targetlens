import type { ReactNode } from "react";

function normalizeMarkdown(content: string) {
  return content
    .replace(/\\([*_`#])/g, "$1")
    // Some provider responses accidentally add one extra pair of asterisks
    // around a bold phrase (****text**). Normalize that before tokenizing.
    .replace(/\*{4}(?=\S)/g, "**")
    .replace(/\*{4}(?=\s|$)/g, "**");
}

function inlineMarkdown(text: string): ReactNode[] {
  const tokenPattern = /(\*\*.+?\*\*|__.+?__|~~.+?~~|`.+?`|\*[^*\n]+?\*|_[^_\n]+?_|(\[[^\]]+\]\((?:https?:\/\/)[^)]+\)))/g;
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = tokenPattern.exec(text)) !== null) {
    if (match.index > lastIndex) nodes.push(text.slice(lastIndex, match.index));
    const token = match[0];
    if (token.startsWith("**") && token.endsWith("**")) nodes.push(<strong key={key++}>{token.slice(2, -2)}</strong>);
    else if (token.startsWith("__") && token.endsWith("__")) nodes.push(<strong key={key++}>{token.slice(2, -2)}</strong>);
    else if (token.startsWith("~~") && token.endsWith("~~")) nodes.push(<del key={key++}>{token.slice(2, -2)}</del>);
    else if (token.startsWith("`") && token.endsWith("`")) nodes.push(<code key={key++}>{token.slice(1, -1)}</code>);
    else if (token.startsWith("*") || token.startsWith("_")) nodes.push(<em key={key++}>{token.slice(1, -1)}</em>);
    else {
      const linkMatch = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
      if (linkMatch) nodes.push(<a key={key++} href={linkMatch[2]} target="_blank" rel="noreferrer">{linkMatch[1]}</a>);
      else nodes.push(token);
    }
    lastIndex = match.index + token.length;
  }
  if (lastIndex < text.length) nodes.push(text.slice(lastIndex));
  return nodes;
}

export function MarkdownContent({ content }: { content: string }) {
  const lines = normalizeMarkdown(content).split(/\r?\n/);
  const blocks: ReactNode[] = [];
  let index = 0;
  let key = 0;

  while (index < lines.length) {
    const line = lines[index].trimEnd();
    if (!line.trim()) {
      index += 1;
      continue;
    }
    if (/^```/.test(line)) {
      const language = line.slice(3).trim();
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      index += 1;
      blocks.push(<pre key={key++}><code data-language={language || undefined}>{codeLines.join("\n")}</code></pre>);
      continue;
    }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const Heading = `h${heading[1].length}` as "h1" | "h2" | "h3";
      blocks.push(<Heading key={key++}>{inlineMarkdown(heading[2])}</Heading>);
      index += 1;
      continue;
    }
    if (/^>\s?/.test(line)) {
      const quoteLines: string[] = [];
      while (index < lines.length && /^>\s?/.test(lines[index])) {
        quoteLines.push(lines[index].replace(/^>\s?/, ""));
        index += 1;
      }
      blocks.push(<blockquote key={key++}>{quoteLines.map((item) => <p key={item}>{inlineMarkdown(item)}</p>)}</blockquote>);
      continue;
    }
    const listMatch = line.match(/^\s*([-*]|\d+[.)])\s+(.+)$/);
    if (listMatch) {
      const ordered = /^\d/.test(listMatch[1]);
      const items: string[] = [];
      while (index < lines.length) {
        const itemMatch = lines[index].match(/^\s*([-*]|\d+[.)])\s+(.+)$/);
        if (!itemMatch || /^\d/.test(itemMatch[1]) !== ordered) break;
        items.push(itemMatch[2]);
        index += 1;
      }
      const List = ordered ? "ol" : "ul";
      blocks.push(<List key={key++}>{items.map((item, itemIndex) => <li key={`${item}-${itemIndex}`}>{inlineMarkdown(item)}</li>)}</List>);
      continue;
    }
    if (/^(---+|\*\*\*+)$/.test(line.trim())) {
      blocks.push(<hr key={key++} />);
      index += 1;
      continue;
    }
    const paragraph: string[] = [line];
    index += 1;
    while (index < lines.length && lines[index].trim() && !/^(#{1,3})\s+/.test(lines[index]) && !/^\s*([-*]|\d+[.)])\s+/.test(lines[index]) && !/^```/.test(lines[index]) && !/^>\s?/.test(lines[index])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push(<p key={key++}>{inlineMarkdown(paragraph.join(" "))}</p>);
  }

  return <div className="markdown-content">{blocks}</div>;
}
