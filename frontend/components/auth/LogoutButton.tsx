"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { clearToken } from "@/lib/token-storage";

export function LogoutButton() {
  const router = useRouter();

  function logout() {
    clearToken();
    toast.success("Signed out of ACRA.");
    router.replace("/login");
  }

  return (
    <button
      type="button"
      onClick={logout}
      className="border border-hairline px-2.5 py-1 font-mono text-[10px] tracking-[0.12em] text-text-muted transition-colors hover:border-hairline-bright hover:bg-panel-raised hover:text-text"
    >
      LOG OUT
    </button>
  );
}
