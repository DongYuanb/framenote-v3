import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import BackgroundGrid from "@/components/BackgroundGrid";
import EdgeOrnaments from "@/components/EdgeOrnaments";
import TestimonialGrid from "@/components/TestimonialGrid";
import UploadDialog from "@/components/UploadDialog";
import LoginGuard from "@/components/LoginGuard";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Download, Github, Bolt, Users, Brain, Video, Link as LinkIcon, Upload, Sparkles, FileDown, FileText, Image as ImageIcon, ShieldCheck, Languages } from "lucide-react";
import { useEffect, useState } from "react";
import { useI18n } from "@/lib/i18n";
import { useAuth } from "@/lib/auth";
import OnlineDownloader from "@/components/OnlineDownloader";
const Index = () => {
  const [openUpload, setOpenUpload] = useState(false);
  const { user } = useAuth();
  const logo = "/lovable-uploads/1a269a26-9009-4b73-80c2-654445d2810b.png";
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "FrameNote",
    applicationCategory: "EducationalApplication",
    operatingSystem: "Web, macOS, Linux, Windows",
    description: "AI 视频笔记工具：一键提取PPT、自动生成讲义与知识图片，极速体验，隐私安全。",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" }
  };

  const { t, lang } = useI18n();

  useEffect(() => {
    document.title = t("seo.index.title");
    const ensure = (name: string) => {
      let el = document.querySelector(`meta[name="${name}"]`);
      if (!el) {
        el = document.createElement("meta");
        el.setAttribute("name", name);
        document.head.appendChild(el);
      }
      return el as HTMLMetaElement;
    };
    ensure("description").setAttribute("content", t("seo.index.desc"));

    let link = document.querySelector('link[rel="canonical"]');
    if (!link) {
      link = document.createElement("link");
      link.setAttribute("rel", "canonical");
      document.head.appendChild(link);
    }
    link.setAttribute("href", window.location.origin + "/");
  }, [t, lang]);
  return (
    <div className="relative min-h-screen bg-background paper-noise">
      <EdgeOrnaments />
      {/* Global AppHeader is rendered in App.tsx */}

      <UploadDialog open={openUpload} onOpenChange={setOpenUpload} />


      <main>
        <section className="relative overflow-hidden grid-stripes">
          <BackgroundGrid />
          <div className="container mx-auto relative z-10 py-24 md:py-32 text-center">
            <p className="mb-6 flex items-center justify-center gap-3 text-xs md:text-sm text-primary">
              <Video className="h-4 w-4" aria-hidden /> {t("upload.local")}
              <span className="opacity-40">·</span>
              <LinkIcon className="h-4 w-4" aria-hidden /> {t("upload.online")}
            </p>
            <h1 className="text-4xl md:text-6xl lg:text-7xl leading-tight tracking-tight text-primary animate-enter font-semibold">
              {t("hero.title")}
            </h1>
            <p className="mt-6 max-w-2xl mx-auto text-base md:text-lg text-muted-foreground">
              {t("hero.subtitle")}
            </p>

            <div className="mt-10 flex items-center justify-center gap-4">
              <Button variant="hero" size="lg" className="hover-scale" onClick={() => setOpenUpload(true)}>
                <Upload /> {t("hero.upload")}
                <Badge variant="secondary" className="ml-1">New</Badge>
              </Button>
              <Button variant="outline" size="lg" className="hover-scale" asChild>
                <a href="#demo">
                  <Github className="mr-1" /> {t("hero.demo")}
                </a>
              </Button>
            </div>

            {/* 登录提示 */}
            {!user && (
              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  使用功能前请先 <a href="/login" className="text-primary underline">登录</a>
                </p>
              </div>
            )}

            {/* Online video URL downloader */}
            <div className="container mx-auto max-w-3xl">
              <OnlineDownloader />
            </div>
          </div>
        </section>

        <section id="features" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <FileText className="text-primary" />
                  <h3 className="font-medium">{t("features.title.1")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("features.desc.1")}</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <Sparkles className="text-primary" />
                  <h3 className="font-medium">{t("features.title.2")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("features.desc.2")}</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <ImageIcon className="text-primary" />
                  <h3 className="font-medium">{t("features.title.3")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("features.desc.3")}</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <Bolt className="text-primary" />
                  <h3 className="font-medium">{t("features.title.4")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("features.desc.4")}</p>
              </article>
            </div>
          </div>
        </section>

        <section id="demo" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <article className="rounded-lg border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <Upload className="text-primary" />
                  <h3 className="font-medium">{t("steps.1")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("steps.1.desc")}</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <Brain className="text-primary" />
                  <h3 className="font-medium">{t("steps.2")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("steps.2.desc")}</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <FileDown className="text-primary" />
                  <h3 className="font-medium">{t("steps.3")}</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{t("steps.3.desc")}</p>
              </article>
            </div>
          </div>
        </section>

        <section id="testimonials" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <TestimonialGrid />
          </div>
        </section>

        <section id="highlights" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-sm">
              <div className="rounded-md border bg-card p-3 flex items-center gap-2"><ShieldCheck className="text-primary" /> {t("high.1")}</div>
              <div className="rounded-md border bg-card p-3 flex items-center gap-2"><Sparkles className="text-primary" /> {t("high.2")}</div>
              <div className="rounded-md border bg-card p-3 flex items-center gap-2"><Languages className="text-primary" /> {t("high.3")}</div>
              <div className="rounded-md border bg-card p-3 flex items-center gap-2"><ShieldCheck className="text-primary" /> {t("high.4")}</div>
            </div>
          </div>
        </section>

        <section id="faq" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <h2 className="text-xl font-semibold">{t("faq.title")}</h2>
            <div className="mt-4">
              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="item-1">
                  <AccordionTrigger>{t("faq.q1")}</AccordionTrigger>
                  <AccordionContent>{t("faq.a1")}</AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-2">
                  <AccordionTrigger>{t("faq.q2")}</AccordionTrigger>
                  <AccordionContent>{t("faq.a2")}</AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-3">
                  <AccordionTrigger>{t("faq.q3")}</AccordionTrigger>
                  <AccordionContent>{t("faq.a3")}</AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t">
        <div className="container mx-auto py-8 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} {t("brand.name")} · {t("footer.copyright")}</p>
        </div>
      </footer>

      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
    </div>
  );
};

export default Index;
