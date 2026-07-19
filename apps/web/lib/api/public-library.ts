export type PublicLibrarySectionKey = "biology" | "expression" | "drugability" | "drugs" | "clinical" | "risk";

export interface PublicLibraryTarget {
  symbol: string;
  name: string;
  aliases: string[];
}

export interface PublicLibrarySource {
  id: string;
  title: string;
  organization: string;
  url: string;
  license: string;
}

export interface PublicLibrarySection {
  key: PublicLibrarySectionKey;
  title: string;
  summary: string;
  points: string[];
}

export interface PublicLibrarySummary {
  slug: string;
  target: PublicLibraryTarget;
  headline: string;
  summary: string;
  updated_at: string;
  source_count: number;
  access_scope: "public";
}

export interface PublicLibraryEntry extends PublicLibrarySummary {
  sections: PublicLibrarySection[];
  sources: PublicLibrarySource[];
  disclaimer: string;
}

const baseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace("://localhost", "://127.0.0.1");

async function requestPublic<T>(path: string): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "GET",
    credentials: "omit",
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`Public library API ${response.status}`);
  return response.json() as Promise<T>;
}

export function listPublicLibrary(): Promise<PublicLibrarySummary[]> {
  return requestPublic<PublicLibrarySummary[]>("/api/v1/public/library");
}

export function getPublicLibraryEntry(slug: string): Promise<PublicLibraryEntry> {
  return requestPublic<PublicLibraryEntry>(`/api/v1/public/library/${encodeURIComponent(slug)}`);
}
