import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

vi.mock("@/lib/token-storage", () => ({
  clearToken: vi.fn(),
  loadToken: () => null,
}));

vi.mock("@/services/auth-service", () => ({
  AuthService: { getCurrentUser: vi.fn() },
}));

import { AuthGuard } from "@/components/auth/AuthGuard";


test("redirects unauthenticated users to login", async () => {
  render(<AuthGuard><p>Protected content</p></AuthGuard>);

  await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
});
