import { httpClient } from "@/lib/api/http-client";
import { mockClient } from "@/lib/api/mock-client";
import type { TargetLensClient } from "@/lib/api/client";

export const targetLensClient: TargetLensClient = process.env.NEXT_PUBLIC_USE_MOCKS === "false" ? httpClient : mockClient;
export type { AskInput, CreateSessionInput, ResearchInput, ResearchJob, TargetLensClient } from "@/lib/api/client";
