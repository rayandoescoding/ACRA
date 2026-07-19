"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { clearToken, loadToken } from "@/lib/token-storage";
import { AuthService } from "@/services/auth-service";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (!loadToken()) {
      router.replace("/login");
      return;
    }

    let active = true;

    AuthService.getCurrentUser()
      .then(() => {
        if (active) setIsAuthenticated(true);
      })
      .catch(() => {
        clearToken();
        router.replace("/login");
      })
      .finally(() => {
        if (active) setIsChecking(false);
      });

    return () => {
      active = false;
    };
  }, [router]);

  if (isChecking || !isAuthenticated) {
    return (
      <main className="grid min-h-screen place-items-center bg-bg px-5">
        <p className="font-mono text-xs tracking-[0.14em] text-text-muted">VERIFYING OPERATOR ACCESS…</p>
      </main>
    );
  }

  return <>{children}</>;
}
