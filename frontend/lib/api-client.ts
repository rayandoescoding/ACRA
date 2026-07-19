import { loadToken } from "@/lib/token-storage";

const configuredBaseUrl = process.env.NEXT_PUBLIC_ACRA_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiRequestOptions = Omit<RequestInit, "headers"> & {
  headers?: HeadersInit;
};

export async function apiClient<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = loadToken();

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null) as { detail?: string } | null;
    throw new ApiError(errorPayload?.detail ?? "The request could not be completed.", response.status);
  }

  return response.json() as Promise<T>;
}
