import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getCurrentUser, loginWithPassword, logout, getMembershipInfo, sendSmsCode, verifySmsCode, setPassword, type User, type Membership } from "./api";

type AuthContextValue = {
  user: User | null;
  membership: Membership | null;
  loading: boolean;
  token: string | null;
  // 短信验证码登录
  sendSms: (phone: string) => Promise<{ message: string; code?: string }>;
  verifySms: (phone: string, code: string) => Promise<{ need_set_password: boolean }>;
  setUserPassword: (password: string) => Promise<void>;
  // 密码登录
  loginWithPassword: (phone: string, password: string) => Promise<void>;
  // 通用
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [membership, setMembership] = useState<Membership | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  });

  const refresh = useCallback(async () => {
    if (!token) {
      setUser(null);
      setMembership(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const u = await getCurrentUser(token).catch(() => null);
      setUser(u);
      const m = u ? await getMembershipInfo(token).catch(() => null) : null;
      setMembership(m);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const sendSms = useCallback(async (phone: string) => {
    return await sendSmsCode(phone);
  }, []);

  const verifySms = useCallback(async (phone: string, code: string) => {
    const result = await verifySmsCode(phone, code);
    setToken(result.token);
    setUser(result.user);
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', result.token);
    }
    return { need_set_password: result.need_set_password };
  }, []);

  const setUserPassword = useCallback(async (password: string) => {
    if (!token) throw new Error("请先登录");
    await setPassword(token, password);
    // 更新用户信息
    await refresh();
  }, [token, refresh]);

  const doLoginWithPassword = useCallback(async (phone: string, password: string) => {
    const result = await loginWithPassword(phone, password);
    setToken(result.token);
    setUser(result.user);
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', result.token);
    }
    await refresh();
  }, [refresh]);

  const doLogout = useCallback(async () => {
    if (token) {
      await logout(token).catch(() => {}); // 忽略退出失败
    }
    setToken(null);
    setUser(null);
    setMembership(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }, [token]);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    membership,
    loading,
    token,
    sendSms,
    verifySms,
    setUserPassword,
    loginWithPassword: doLoginWithPassword,
    logout: doLogout,
    refresh
  }), [user, membership, loading, token, sendSms, verifySms, setUserPassword, doLoginWithPassword, doLogout, refresh]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


