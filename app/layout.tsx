import type { Metadata } from "next";
import { Fraunces, Geist_Mono, Noto_Serif_SC, Outfit } from "next/font/google";
import { SiteFooter, SiteHeader } from "@/components/site-header";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
});

const noto = Noto_Serif_SC({
  variable: "--font-noto",
  subsets: ["latin"],
  weight: ["500", "600"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Si Zhen Desk",
    template: "%s · Si Zhen Desk",
  },
  description:
    "A teaching workbench for traditional Chinese medicine syndrome differentiation, built from three parent papers on multi-label, sparse, and holistic pattern classification.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${outfit.variable} ${fraunces.variable} ${noto.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <TooltipProvider>
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </TooltipProvider>
      </body>
    </html>
  );
}
