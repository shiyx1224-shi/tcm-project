"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const links = [
  { href: "/", label: "Home" },
  { href: "/explorer", label: "Syndrome Explorer" },
  { href: "/results", label: "Research Results" },
  { href: "/about", label: "About Research" },
]

export function SiteHeader() {
  const pathname = usePathname()

  return (
    <header className="border-b border-[color-mix(in_srgb,var(--wood)_40%,transparent)] bg-[color-mix(in_srgb,var(--warm-white)_88%,transparent)] backdrop-blur-sm">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-3.5 sm:flex-row sm:items-center sm:justify-between">
        <Link href="/" className="flex items-center gap-3">
          <span className="seal-mark size-9 rounded-sm text-sm">辨</span>
          <span>
            <span className="font-heading block text-base leading-tight tracking-tight text-ink">
              TCM Syndrome Desk
            </span>
            <span className="font-cjk text-[11px] text-muted-foreground">中医辨证 · 机器学习研究</span>
          </span>
        </Link>
        <nav className="flex gap-1 overflow-x-auto pb-0.5">
          {links.map((link) => {
            const active = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm whitespace-nowrap transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                )}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>
      </div>
      <p className="border-t border-[color-mix(in_srgb,var(--wood)_25%,transparent)] px-4 py-1.5 text-center text-[11px] text-muted-foreground">
        Educational research instrument · not a clinical diagnosis tool
      </p>
    </header>
  )
}

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-[color-mix(in_srgb,var(--wood)_35%,transparent)] px-4 py-6 text-center text-xs text-muted-foreground">
      <p>
        Teaching-pattern coverage scores are educational demonstrations, not clinical probabilities and not
        TCM-SD model outputs.
      </p>
      <p className="mt-2">
        DS340W ·{" "}
        <a
          className="text-primary underline-offset-2 hover:underline"
          href="https://github.com/shiyx1224-shi/tcm-project"
          target="_blank"
          rel="noreferrer"
        >
          shiyx1224-shi/tcm-project
        </a>
      </p>
    </footer>
  )
}
