import { apiClient } from "@/lib/api-client";

export type UserRole = "admin" | "support_agent";

export type LoginCredentials = {
  email: string;
  password: string;
};

export type AccessToken = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
};

export type AuthenticatedUser = {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
};

export const AuthService = {
  login(credentials: LoginCredentials): Promise<AccessToken> {
    return apiClient<AccessToken>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },

  getCurrentUser(): Promise<AuthenticatedUser> {
    return apiClient<AuthenticatedUser>("/auth/me");
  },
};
