import { useAuth } from "@/lib/auth";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

interface LoginGuardProps {
  children: React.ReactNode;
}

export default function LoginGuard({ children }: LoginGuardProps) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // 会重定向到登录页
  }

  return <>{children}</>;
}
