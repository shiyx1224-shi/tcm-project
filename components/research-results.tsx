import Image from "next/image"
import Link from "next/link"

const validationRows = [
  { model: "SVM (LinearSVC)", accuracy: "0.7517", micro: "0.7517", macro: "0.4745", selected: true },
  { model: "Random Forest", accuracy: "0.7314", micro: "0.7314", macro: "0.4312", selected: false },
  { model: "Logistic Regression", accuracy: "0.5120", micro: "0.5120", macro: "0.3316", selected: false },
  { model: "Chen-inspired BERT+CNN", accuracy: "0.5007", micro: "0.5007", macro: "0.2521", selected: false },
  { model: "Huang-inspired CNN", accuracy: "0.4635", micro: "0.4635", macro: "0.2112", selected: false },
]

export function ResearchResults() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <p className="text-xs tracking-[0.16em] text-primary uppercase">Research Results</p>
      <h1 className="font-heading mt-1 text-3xl tracking-tight text-ink">Measured ML evaluation</h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        All figures below are from the TCM-SD experiments in this repository. Model selection used validation
        micro-F1 only; the held-out test set was scored once for the selected SVM.
      </p>

      <section className="mt-10">
        <h2 className="font-heading text-xl text-ink">Validation leaderboard</h2>
        <div className="mt-4 overflow-x-auto rounded-xl border border-wood/30 bg-card">
          <table className="w-full min-w-[32rem] text-left text-sm">
            <thead className="border-b border-wood/25 bg-secondary/50 text-xs tracking-wide text-muted-foreground uppercase">
              <tr>
                <th className="px-4 py-3 font-medium">Model</th>
                <th className="px-4 py-3 font-medium">Accuracy</th>
                <th className="px-4 py-3 font-medium">Micro-F1</th>
                <th className="px-4 py-3 font-medium">Macro-F1</th>
              </tr>
            </thead>
            <tbody>
              {validationRows.map((row) => (
                <tr key={row.model} className="border-b border-wood/15 last:border-0">
                  <td className="px-4 py-3">
                    {row.model}
                    {row.selected && (
                      <span className="ml-2 rounded-sm bg-primary/10 px-1.5 py-0.5 text-[11px] text-primary">
                        selected
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 tabular-nums">{row.accuracy}</td>
                  <td className="px-4 py-3 tabular-nums">{row.micro}</td>
                  <td className="px-4 py-3 tabular-nums">{row.macro}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-10 grid gap-4 sm:grid-cols-2">
        <MetricCard title="Validation (SVM)" lines={["Accuracy 0.7517", "Micro-F1 0.7517", "Macro-F1 0.4745"]} />
        <MetricCard
          title="Held-out test (SVM)"
          lines={["Accuracy 0.7548", "Micro-F1 0.7548", "Macro-F1 0.4992", "n = 10,777"]}
          accent
        />
      </section>

      <section className="mt-10">
        <h2 className="font-heading text-xl text-ink">Figures</h2>
        <div className="mt-4 grid gap-6">
          <Figure
            src="/results/figures/model_comparison.png"
            alt="Model comparison chart"
            caption="Validation comparison across baselines and deep adaptations."
          />
          <Figure
            src="/results/figures/final_f1_comparison.png"
            alt="Final F1 comparison"
            caption="Selected SVM: validation vs held-out test F1."
          />
          <Figure
            src="/results/figures/final_test_confusion_top15.png"
            alt="Top-15 confusion matrix"
            caption="Test confusion among the most frequent syndromes."
          />
        </div>
      </section>

      <section className="mt-10 rounded-xl border border-wood/30 bg-card p-5 text-sm leading-relaxed text-muted-foreground">
        <h2 className="font-heading text-base text-ink">Method snapshot</h2>
        <ul className="mt-3 list-disc space-y-1 pl-5">
          <li>Leakage-aware 70 / 10 / 20 split by patient and clinical-text fingerprint.</li>
          <li>Train-only TF-IDF + SelectKBest (χ², k=5000) for classical models.</li>
          <li>Huang- and Chen-inspired networks are adaptations, not exact paper reproductions.</li>
          <li>
            Full write-up:{" "}
            <Link href="/about" className="text-primary underline-offset-2 hover:underline">
              About Research
            </Link>{" "}
            ·{" "}
            <a
              href="https://github.com/shiyx1224-shi/tcm-project/blob/main/docs/final_evaluation.md"
              className="text-primary underline-offset-2 hover:underline"
              target="_blank"
              rel="noreferrer"
            >
              final_evaluation.md
            </a>
          </li>
        </ul>
      </section>
    </div>
  )
}

function MetricCard({ title, lines, accent }: { title: string; lines: string[]; accent?: boolean }) {
  return (
    <div
      className={`rounded-xl border p-5 ${
        accent ? "border-primary/40 bg-[color-mix(in_srgb,var(--herbal)_8%,var(--warm-white))]" : "border-wood/30 bg-card"
      }`}
    >
      <h3 className="font-heading text-base text-ink">{title}</h3>
      <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
        {lines.map((line) => (
          <li key={line} className="tabular-nums">
            {line}
          </li>
        ))}
      </ul>
    </div>
  )
}

function Figure({ src, alt, caption }: { src: string; alt: string; caption: string }) {
  return (
    <figure className="overflow-hidden rounded-xl border border-wood/30 bg-card">
      <div className="relative aspect-[16/9] w-full bg-secondary/40">
        <Image src={src} alt={alt} fill className="object-contain p-3" sizes="(max-width: 1024px) 100vw, 960px" />
      </div>
      <figcaption className="border-t border-wood/20 px-4 py-3 text-sm text-muted-foreground">{caption}</figcaption>
    </figure>
  )
}
