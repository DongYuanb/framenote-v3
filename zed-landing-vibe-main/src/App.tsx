import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { LanguageProvider } from "@/lib/i18n";
import AppHeader from "@/components/AppHeader";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Result from "./pages/Result";
import Login from "./pages/Login";
import Account from "./pages/Account";
import Vip from "./pages/Vip";
const queryClient = new QueryClient();

import { LayoutProvider, LayoutContainer } from "@/lib/layout";
const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <LanguageProvider>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <LayoutProvider>
            <BrowserRouter>
              <LayoutContainer>
                <AppHeader />
                <Routes>
                  <Route path="/" element={<Index />} />
                  <Route path="/result/:taskId" element={<Result />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/account" element={<Account />} />
                  <Route path="/vip" element={<Vip />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </LayoutContainer>
            </BrowserRouter>
          </LayoutProvider>
        </ThemeProvider>
      </LanguageProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
