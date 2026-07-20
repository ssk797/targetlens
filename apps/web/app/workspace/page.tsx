import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { AuthGate } from "@/components/auth/auth-gate";

export default function WorkspacePage() {
  return <AuthGate><WorkspaceShell /></AuthGate>;
}
