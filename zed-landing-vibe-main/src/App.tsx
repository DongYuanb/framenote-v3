import React from 'react'
import { Toaster } from "@/components/ui/toaster"
import { TooltipProvider } from "@/components/ui/tooltip"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ThemeProvider } from "next-themes"
import { LanguageProvider } from "@/lib/i18n"
import { LayoutProvider, LayoutContainer } from "@/lib/layout"
import AppHeader from "@/components/AppHeader"
import Index from "./pages/Index"
import NotFound from "./pages/NotFound"
import Result from "./pages/Result"
import TestBackground from "./components/TestBackground"

const queryClient = new QueryClient()

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <LanguageProvider>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <LayoutProvider>
            <BrowserRouter>
              <LayoutContainer>
                <AppHeader />
                <Routes>
                  <Route path="/" element={<Index />} />
                  <Route path="/result/:taskId" element={<Result />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </LayoutContainer>
            </BrowserRouter>
          </LayoutProvider>
        </ThemeProvider>
      </LanguageProvider>
    </TooltipProvider>
  </QueryClientProvider>
)

export default App