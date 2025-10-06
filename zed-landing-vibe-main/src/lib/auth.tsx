import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getCurrentUser, loginWithPassword, logout, getMembershipInfo, type User, type Membership } from "./api";

type AuthContextValue = {
  user: User | null;
  membership: Membership | null;
  loading: boolean;
  login: (p: { username: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [membership, setMembership] = useState<Membership | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const u = await getCurrentUser().catch(() => null);
      setUser(u);
      const m = u ? await getMembershipInfo().catch(() => null) : null;
      setMembership(m);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const doLogin = useCallback(async ({ username, password }: { username: string; password: string }) => {
    await loginWithPassword(username, password);
    await refresh();
  }, [refresh]);

  const doLogout = useCallback(async () => {
    await logout();
    await refresh();
  }, [refresh]);

  const value = useMemo<AuthContextValue>(() => ({ user, membership, loading, login: doLogin, logout: doLogout, refresh }), [user, membership, loading, doLogin, doLogout, refresh]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


