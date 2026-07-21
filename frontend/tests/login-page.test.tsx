import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn() }),
}));

vi.mock("@/services/auth-service", () => ({
  AuthService: { login: vi.fn() },
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import LoginPage from "@/app/login/page";
import { AuthService } from "@/services/auth-service";
import { toast } from "sonner";

beforeEach(() => vi.clearAllMocks());

test("renders the operator login form", () => {
  render(<LoginPage />);

  expect(screen.getByRole("heading", { name: "Sign in to the console" })).toBeInTheDocument();
  expect(screen.getByLabelText("EMAIL")).toBeInTheDocument();
  expect(screen.getByLabelText("PASSWORD")).toBeInTheDocument();
});

test("keeps the accessible login error and shows a failure toast", async () => {
  vi.mocked(AuthService.login).mockRejectedValue(new Error("offline"));
  render(<LoginPage />);

  fireEvent.change(screen.getByLabelText("EMAIL"), { target: { value: "operator@example.com" } });
  fireEvent.change(screen.getByLabelText("PASSWORD"), { target: { value: "password" } });
  fireEvent.click(screen.getByRole("button", { name: "SIGN IN" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("Unable to sign in. Please try again.");
  await waitFor(() => expect(toast.error).toHaveBeenCalledWith("Unable to sign in. Please try again."));
});
