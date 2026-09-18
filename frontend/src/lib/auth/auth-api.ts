import { apiClient } from "@/lib/api/client";

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user?: {
    id: number;
    email: string;
    name: string;
    role: string;
    avatar_url?: string | null;
  };
};

export async function loginRequest(payload: LoginPayload): Promise<LoginResponse> {
  const formData = new URLSearchParams();

  formData.append("username", payload.email);
  formData.append("password", payload.password);

  const { data } = await apiClient.post<LoginResponse>("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return data;
}

// The current FastAPI backend deliberately has no password-reset endpoints.
// Keep these public screens truthful instead of calling a non-existent API.
export async function requestPasswordResetLink(_email: string): Promise<void> {
  throw new Error("Password reset is not available from this backend yet.");
}

export async function submitNewPassword(_input: {
  token: string;
  password: string;
}): Promise<void> {
  throw new Error("Password reset is not available from this backend yet.");
}
