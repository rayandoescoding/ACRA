"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { ApiError } from "@/lib/api-client";
import { saveToken } from "@/lib/token-storage";
import { AuthService } from "@/services/auth-service";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const token = await AuthService.login({ email, password });
      saveToken(token.access_token);
      toast.success("Operator access verified.");
      router.replace("/");
    } catch (caughtError) {
      const message = caughtError instanceof ApiError ? caughtError.message : "Unable to sign in. Please try again.";
      setError(message);
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-bg px-5 py-10">
      <section className="w-full max-w-md border border-hairline bg-panel p-6 shadow-2xl sm:p-8" aria-labelledby="login-title">
        <div className="flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center border border-teal bg-teal-dim font-mono text-sm font-bold text-teal">A</span>
          <div>
            <p className="font-mono text-sm font-semibold tracking-[0.2em] text-text">ACRA</p>
            <p className="font-mono text-[9px] tracking-[0.12em] text-text-faint">AGENT CONTROL ROOM</p>
          </div>
        </div>

        <div className="mt-10">
          <p className="font-mono text-[10px] tracking-[0.14em] text-blue-signal">OPERATOR AUTHENTICATION</p>
          <h1 id="login-title" className="mt-2 text-2xl font-semibold text-text">Sign in to the console</h1>
          <p className="mt-2 text-sm leading-6 text-text-muted">Use your internal ACRA operator credentials to continue.</p>
        </div>

        <form className="mt-8 space-y-5" onSubmit={submit}>
          <label className="block">
            <span className="font-mono text-[10px] tracking-[0.12em] text-text-faint">EMAIL</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full border border-hairline bg-bg px-3 py-2.5 text-sm text-text outline-none transition-colors placeholder:text-text-faint focus:border-blue-signal focus:bg-panel-raised"
              autoComplete="email"
              required
            />
          </label>

          <label className="block">
            <span className="font-mono text-[10px] tracking-[0.12em] text-text-faint">PASSWORD</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full border border-hairline bg-bg px-3 py-2.5 text-sm text-text outline-none transition-colors placeholder:text-text-faint focus:border-blue-signal focus:bg-panel-raised"
              autoComplete="current-password"
              required
            />
          </label>

          {error && (
            <p className="border border-coral bg-coral-dim px-3 py-2 font-mono text-xs text-coral" role="alert">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full border border-teal bg-teal-dim px-4 py-3 font-mono text-xs font-semibold tracking-[0.14em] text-teal transition-colors hover:bg-panel-raised disabled:cursor-not-allowed disabled:border-hairline disabled:text-text-faint"
          >
            {isSubmitting ? "VERIFYING…" : "SIGN IN"}
          </button>
        </form>
      </section>
    </main>
  );
}
