import Link from "next/link"
import { Button } from "@/components/ui/button"

const workflow = [
  "Clinical Data",
  "Preprocessing",
  "Machine Learning",
  "Syndrome Classification",
  "Evaluation",
]

export function HomeLanding() {
  return (
    <div className="mx-auto max-w-5xl px-4 pb-16 pt-10 sm:pt-14">
      <section className="relative overflow-hidden rounded-xl border border-[color-mix(in_srgb,var(--wood)_35%,transparent)] bg-card px-6 py-12 sm:px-12 sm:py-16">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 w-1/3 bg-[radial-gradient(circle_at_70%_40%,rgba(66,102,83,0.1),transparent_70%)]"
        />
        <p className="font-cjk text-sm tracking-[0.2em] text-primary">中医辨证 · 机器学习研究</p>
        <h1 className="font-heading mt-3 max-w-3xl text-3xl leading-tight tracking-tight text-ink sm:text-4xl">
          Traditional Chinese Medicine Syndrome Classification
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
          Exploring how machine learning identifies TCM syndromes from patient symptoms and clinical information.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild size="lg" className="rounded-md">
            <Link href="/explorer">Explore Syndromes</Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="rounded-md border-wood/50">
            <Link href="/results">View Research Results</Link>
          </Button>
        </div>
      </section>

      <section className="mt-14 grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <h2 className="font-heading text-xl text-ink">Research overview</h2>
          <ul className="mt-4 space-y-3 text-sm leading-relaxed text-muted-foreground">
            <li>
              <span className="font-medium text-foreground">Problem. </span>
              Can models classify TCM syndromes from free-text symptoms and clinical notes on a public benchmark?
            </li>
            <li>
              <span className="font-medium text-foreground">Why it matters. </span>
              Syndrome differentiation (辨证) organizes signs into patterns that guide holistic reading—not a single
              disease label.
            </li>
            <li>
              <span className="font-medium text-foreground">This study. </span>
              We evaluate classical ML and parent-paper–inspired deep adaptations on TCM-SD (148 syndromes), with a
              locked validation→test protocol.
            </li>
          </ul>
        </div>

        <div className="rounded-xl border border-[color-mix(in_srgb,var(--wood)_30%,transparent)] bg-card p-5">
          <h3 className="font-heading text-sm tracking-wide text-ink uppercase">Research workflow</h3>
          <ol className="mt-4 space-y-0">
            {workflow.map((step, index) => (
              <li key={step} className="relative flex gap-3 pb-5 last:pb-0">
                {index < workflow.length - 1 && (
                  <span aria-hidden className="absolute top-6 left-[0.7rem] h-[calc(100%-1.25rem)] w-px bg-wood/35" />
                )}
                <span className="mt-0.5 grid size-6 shrink-0 place-items-center rounded-full bg-primary text-[11px] text-primary-foreground">
                  {index + 1}
                </span>
                <span className="pt-0.5 text-sm text-foreground">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="mt-14 border-t border-[color-mix(in_srgb,var(--wood)_30%,transparent)] pt-10">
        <div className="grid gap-6 sm:grid-cols-3">
          <QuickLink
            href="/explorer"
            title="Syndrome Explorer"
            blurb="Four examinations, sample charts, and teaching-pattern readings."
          />
          <QuickLink
            href="/results"
            title="Measured results"
            blurb="Validation leaderboard, selected SVM test metrics, and figures."
          />
          <QuickLink
            href="/about"
            title="About the study"
            blurb="Dataset, parent papers, methods, and source repository."
          />
        </div>
      </section>
    </div>
  )
}

function QuickLink({ href, title, blurb }: { href: string; title: string; blurb: string }) {
  return (
    <Link
      href={href}
      className="group rounded-xl border border-[color-mix(in_srgb,var(--wood)_28%,transparent)] bg-card p-5 transition-colors hover:border-primary/50"
    >
      <h3 className="font-heading text-base text-ink group-hover:text-primary">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{blurb}</p>
    </Link>
  )
}
