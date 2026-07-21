import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, vi } from "vitest";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

vi.mock("@/lib/token-storage", () => ({
  clearToken: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn() },
}));

import { LogoutButton } from "@/components/auth/LogoutButton";
import { clearToken } from "@/lib/token-storage";
import { toast } from "sonner";

beforeEach(() => vi.clearAllMocks());

test("clears the session and confirms logout", () => {
  render(<LogoutButton />);

  fireEvent.click(screen.getByRole("button", { name: "LOG OUT" }));

  expect(clearToken).toHaveBeenCalledOnce();
  expect(toast.success).toHaveBeenCalledWith("Signed out of ACRA.");
  expect(replace).toHaveBeenCalledWith("/login");
});
