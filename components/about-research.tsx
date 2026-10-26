import Link from "next/link"

export function AboutResearch() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <p className="text-xs tracking-[0.16em] text-qing uppercase">About Research</p>
      <h1 className="font-heading mt-1 text-3xl tracking-tight text-ink">Study context and sources</h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        DS340W project on public TCM-SD syndrome classification, with a teaching desk for four-examination pattern
        reading inspired by three verified parent papers.
      </p>

      <section className="mt-10 space-y-3">
        <h2 className="font-heading text-xl text-ink">Dataset</h2>
        <div className="rounded-xl border border-wood/30 bg-card p-5 text-sm leading-relaxed">
          <p>
            <span className="font-medium text-foreground">TCM-SD</span> — 54,152 clinical records → 148{" "}
            <code className="text-xs">norm_syndrome</code> labels.
          </p>
          <p className="mt-2 text-muted-foreground">
            Public link:{" "}
            <a
              className="text-primary underline-offset-2 hover:underline"
              href="https://github.com/Borororo/ZY-BERT"
              target="_blank"
              rel="noreferrer"
            >
              github.com/Borororo/ZY-BERT
            </a>{" "}
            · License CC BY-NC-SA 4.0 · Ren et al., CCL 2022.
          </p>
        </div>
      </section>

      <section className="mt-10 space-y-3">
        <h2 className="font-heading text-xl text-ink">Parent papers</h2>
        <ol className="space-y-3 text-sm leading-relaxed">
          <li className="rounded-xl border border-wood/30 bg-card p-4">
            <p className="font-medium text-foreground">Gong et al., 2023 — Frontiers in Genetics</p>
            <p className="mt-1 text-muted-foreground">
              Multi-label framing; Pearson-inspired symptom ranking adapted for multiclass TCM-SD.
            </p>
          </li>
          <li className="rounded-xl border border-wood/30 bg-card p-4">
            <p className="font-medium text-foreground">Huang et al., 2022 — JMIR Medical Informatics</p>
            <p className="mt-1 text-muted-foreground">
              Cross-feature CNN ideas → AdaptedCrossFGCNN on free-text tokens (not Huang’s private 60-field table).
            </p>
          </li>
          <li className="rounded-xl border border-wood/30 bg-card p-4">
            <p className="font-medium text-foreground">Chen et al., 2024 — Integrative Medicine Research</p>
            <p className="mt-1 text-muted-foreground">
              BERT + TextCNN adaptation with a frozen Chinese encoder (not Chen’s 21-label constraint head).
            </p>
          </li>
        </ol>
      </section>

      <section className="mt-10 space-y-3">
        <h2 className="font-heading text-xl text-ink">Methodology</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-muted-foreground">
          <li>Leakage-aware 70% / 10% / 20% split by patient and clinical fingerprint groups.</li>
          <li>Train-only preprocessing and feature selection; validation selects the model; test is locked.</li>
          <li>
            Interactive Syndrome Explorer uses a separate teaching-pattern engine for demonstration—not the SVM
            pipeline.
          </li>
        </ul>
      </section>

      <section className="mt-10 space-y-3">
        <h2 className="font-heading text-xl text-ink">Site visual language</h2>
        <p className="text-sm leading-relaxed text-muted-foreground">
          The teaching UI uses a restrained 中医五色 palette: rice-paper white (白), ink black (黑) for primary
          actions, muted yellow (黄) for borders, cinnabar (赤) for rare alerts, and slate-blue (青) for small
          labels—kept quiet so the site reads as a research desk, not a decorative motif board.
        </p>
      </section>

      <section className="mt-10 space-y-3">
        <h2 className="font-heading text-xl text-ink">Limitations</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-muted-foreground">
          <li>Deep models are adaptations; parent hospital corpora are not public.</li>
          <li>Macro-F1 remains much lower than micro-F1 under class imbalance.</li>
          <li>Teaching-desk scores must not be read as clinical probabilities or TCM-SD predictions.</li>
        </ul>
      </section>

      <section className="mt-10 flex flex-wrap gap-3">
        <Link
          href="/results"
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-95"
        >
          View research results
        </Link>
        <a
          href="https://github.com/shiyx1224-shi/tcm-project"
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-wood/40 bg-card px-4 py-2 text-sm text-foreground hover:border-primary/50"
        >
          GitHub source
        </a>
      </section>
    </div>
  )
}
