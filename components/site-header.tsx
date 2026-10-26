"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const links = [
  { href: "/", label: "Chart" },
  { href: "/cases", label: "Sample charts" },
  { href: "/atlas", label: "Pattern atlas" },
  { href: "/lab", label: "Teaching lab" },
  { href: "/papers", label: "Parent papers" },
]

export function SiteHeader() {
  const pathname = usePathname()

  return (
    <header className="border-b border-border/80 bg-card/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <Link href="/" className="flex items-center gap-3">
          <span className="font-cjk grid size-10 place-items-center rounded-full border border-primary/40 bg-primary text-sm text-primary-foreground">
            辨
          </span>
          <span>
            <span className="font-heading block text-lg leading-none tracking-tight">Si Zhen Desk</span>
            <span className="text-xs text-muted-foreground">Four examinations · multi-label patterns</span>
          </span>
        </Link>
        <nav className="flex gap-1 overflow-x-auto">
          {links.map((link) => {
            const active = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-full px-3 py-1.5 text-sm whitespace-nowrap",
                  active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                )}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>
      </div>
      <p className="border-t border-border/70 px-4 py-2 text-center text-xs text-muted-foreground">
        Teaching instrument only. It does not diagnose, prescribe, or replace a licensed clinician.
      </p>
    </header>
  )
}

export function SiteFooter() {
  return (
    <footer className="mt-8 border-t border-border/80 px-4 py-6 text-center text-xs text-muted-foreground">
      <p>
        Pattern coverage is how completely a teaching profile is present on the chart. It is not a clinical
        probability and it is not the accuracy reported by the parent studies.
      </p>
      <p className="mt-2">
        DS340W · Si Zhen Desk · intended repo{" "}
        <a
          className="underline-offset-2 hover:underline"
          href="https://github.com/shiyx1224-shi/ds340wproject"
          target="_blank"
          rel="noreferrer"
        >
          shiyx1224-shi/ds340wproject
        </a>
      </p>
    </footer>
  )
}
