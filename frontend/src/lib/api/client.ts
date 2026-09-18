import axios from "axios";

// An empty base URL sends requests to Vite/TanStack Start instead of FastAPI.
// Override this for deployed environments with VITE_API_BASE_URL.
const API_BASE_URL = (import.meta.env["VITE_API_BASE_URL"] || "http://localhost:8000").replace(
  /\/$/,
  "",
);
const TOKEN_KEY = "contractiq_access_token";

let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = readAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      const token = readAccessToken();
      if (token) {
        clearAccessToken();
        onUnauthorized?.();
      }
    }
    return Promise.reject(error);
  },
);

export function readAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(TOKEN_KEY) ?? localStorage.getItem(TOKEN_KEY);
}

export function storeAccessToken(token: string, rememberMe = false) {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
  (rememberMe ? localStorage : sessionStorage).setItem(TOKEN_KEY, token);
}

export function clearAccessToken() {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem("contractiq_refresh_token");
  localStorage.removeItem("contractiq_refresh_token");
  sessionStorage.removeItem("refresh_token");
  localStorage.removeItem("refresh_token");
}

export function clearAuthStorage() {
  if (typeof window === "undefined") return;
  clearAccessToken();
  sessionStorage.removeItem("contractiq_user_email");
  localStorage.removeItem("contractiq_user_email");
}
