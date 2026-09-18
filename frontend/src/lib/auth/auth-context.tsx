import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import {
  apiClient,
  clearAccessToken,
  clearAuthStorage,
  readAccessToken,
  setUnauthorizedHandler,
  storeAccessToken,
} from "@/lib/api/client";
import { loginRequest } from "./auth-api";

export type AuthUser = {
  email: string;
  id?: number;
  role?: string;
  name?: string;
  avatar_url?: string | null;
};

type AuthContextValue = {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  signIn: (input: { email: string; password: string; rememberMe: boolean }) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const USER_KEY = "contractiq_user_email";

function userFromToken(token: string): AuthUser | null {
  try {
    const payload = JSON.parse(
      atob(token.split(".")[1]!.replace(/-/g, "+").replace(/_/g, "/")),
    ) as {
      sub?: string;
      user_id?: number;
      role?: string;
      name?: string;
      avatar_url?: string;
      exp?: number;
    };
    if (!payload.sub || (payload.exp && payload.exp * 1000 <= Date.now())) return null;
    return {
      email: payload.sub,
      ...(payload.user_id !== undefined ? { id: payload.user_id } : {}),
      ...(payload.role !== undefined ? { role: payload.role } : {}),
      ...(payload.name !== undefined ? { name: payload.name } : {}),
      avatar_url: payload.avatar_url ?? null,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  useEffect(() => {
    const existing = readAccessToken();
    if (existing) {
      const restoredUser = userFromToken(existing);
      if (!restoredUser) {
        clearAuthStorage();
      } else {
        setToken(existing);
        setUser(restoredUser);
      }
    }
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearAuthStorage();
      queryClient.clear();
      setToken(null);
      setUser(null);
      window.location.assign("/login?expired=1");
    });
    return () => setUnauthorizedHandler(() => undefined);
  }, [queryClient]);

  const signOut = useCallback(async () => {
    try {
      // 1. Notify backend to log "User Logged Out" activity in PostgreSQL
      await apiClient.post("/auth/logout").catch(() => {});
    } catch {
      // Handle network errors gracefully — never trap user in session
    } finally {
      // 2. Clear JWT access token & refresh tokens from localStorage and sessionStorage
      clearAuthStorage();

      // 3. Clear cached React Query data so sensitive info doesn't persist in memory
      queryClient.clear();

      // 4. Clear React Context state
      setToken(null);
      setUser(null);

      // 5. Redirect user to /login
      navigate({ to: "/login", replace: true });
    }
  }, [navigate, queryClient]);

  const signIn = useCallback(
    async ({
      email,
      password,
      rememberMe,
    }: {
      email: string;
      password: string;
      rememberMe: boolean;
    }) => {
      const result = await loginRequest({ email, password });
      storeAccessToken(result.access_token, rememberMe);
      (rememberMe ? localStorage : sessionStorage).setItem(USER_KEY, email);
      setToken(result.access_token);
      const decoded = userFromToken(result.access_token);
      setUser(
        decoded ?? {
          email,
          name: result.user?.name,
          role: result.user?.role,
          id: result.user?.id,
          avatar_url: result.user?.avatar_url,
        },
      );
    },
    [],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ token, user, isAuthenticated: Boolean(token), isHydrated, signIn, signOut }),
    [token, user, isHydrated, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
