import { TutorialShell } from "@/components/tutorial/tutorial-shell";
import { AuthGate } from "@/components/auth/auth-gate";

export default function TutorialPage() {
  return <AuthGate><TutorialShell /></AuthGate>;
}
