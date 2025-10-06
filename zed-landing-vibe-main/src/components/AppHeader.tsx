import { useI18n } from "@/lib/i18n";
import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sun, Moon, Languages, ChevronDown } from "lucide-react";
import { useTheme } from "next-themes";
import { UserCenter } from "@/components/UserCenter";

const logo = "/lovable-uploads/1a269a26-9009-4b73-80c2-654445d2810b.png";

export default function AppHeader() {
  const { lang, setLang, t } = useI18n();
  const { theme, setTheme, resolvedTheme } = useTheme();

  useEffect(() => {
    // noop: could persist theme if needed (next-themes already does)
  }, [theme]);

  const toggleLang = () => setLang(lang === "zh" ? "en" : "zh");
  const toggleTheme = () => setTheme(resolvedTheme === "dark" ? "light" : "dark");

  // 模拟用户状态
  const mockUser = {
    isLoggedIn: false,
    userInfo: {
      name: '张三',
      email: 'zhangsan@example.com',
      avatar: ''
    }
  };

  return (
    <header className={cn("sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b")}> 
      <nav className="container mx-auto flex items-center justify-between py-3">
        <a href="/" className="flex items-center gap-2" aria-label={t("brand.name")}> 
          <img src={logo} alt={`${t("brand.name")} logo`} className="h-6 w-6" loading="lazy" />
          <span className="text-sm md:text-base font-semibold tracking-tight text-primary">{t("brand.name")}</span>
        </a>
        <div className="flex items-center gap-2 md:gap-3">
          <a href="#features" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">{t("nav.product")}</a>
          <a href="#demo" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">{t("nav.resources")}</a>
          <a href="#faq" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">{t("nav.faq")}</a>

          <Button variant="outline" size="sm" onClick={toggleLang} aria-label="Toggle language" className="flex items-center gap-1">
            <Languages className="h-4 w-4" />
            <span className="text-xs font-medium">{lang === "zh" ? "中" : "EN"}</span>
            <ChevronDown className="h-3 w-3 opacity-60" />
          </Button>

          <Button variant="ghost" size="icon" aria-label="Toggle theme" onClick={toggleTheme}>
            {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          {/* 个人中心 */}
          <UserCenter 
            isLoggedIn={mockUser.isLoggedIn} 
            userInfo={mockUser.userInfo} 
          />
        </div>
      </nav>
    </header>
  );
}
