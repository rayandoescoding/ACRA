"use client";

import { Toaster } from "sonner";

export function ToastProvider() {
  return (
    <Toaster
      closeButton
      position="top-right"
      toastOptions={{
        classNames: {
          toast: "border border-hairline bg-panel text-text shadow-2xl",
          title: "font-mono text-xs font-semibold tracking-[0.1em] text-text",
          description: "font-sans text-sm text-text-muted",
          closeButton: "border-hairline bg-panel text-text-muted hover:bg-panel-raised hover:text-text",
          success: "border-teal bg-teal-dim",
          error: "border-coral bg-coral-dim",
        },
      }}
    />
  );
}
