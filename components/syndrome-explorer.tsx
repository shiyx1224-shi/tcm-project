"use client"

import { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { ResultPanel } from "@/components/result-panel"
import { AtlasView } from "@/components/atlas-view"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { showcaseCases } from "@/lib/cases"
import { analyze, neighborReading, relatedDiseases } from "@/lib/engine"
import { EXAM_CHINESE, EXAM_LABEL, parseSymptomText, symptoms } from "@/lib/symptoms"
import { DOMAIN_META } from "@/lib/syndromes"
import type { Domain, Exam } from "@/lib/types"
import { cn } from "@/lib/utils"

const domains: Domain[] = ["holistic", "kidney", "stomach", "dysmenorrhea"]
const exams: Exam[] = ["inspection", "listening", "inquiry", "palpation"]

type Panel = "chart" | "atlas"

export function SyndromeExplorer({
  initialCaseId,
  initialPanel = "chart",
}: {
  initialCaseId: string | null
  initialPanel?: Panel
}) {
  const router = useRouter()
  const loaded = showcaseCases.find((entry) => entry.id === initialCaseId) ?? null
  const missingCase = Boolean(initialCaseId && !loaded)

  const [panel, setPanel] = useState<Panel>(initialPanel)
  const [step, setStep] = useState<1 | 2 | 3>(loaded ? 3 : 1)
  const [analyzed, setAnalyzed] = useState(Boolean(loaded))
  const [domain, setDomain] = useState<Domain>(loaded?.domain ?? "holistic")
  const [selected, setSelected] = useState<Set<string>>(new Set(loaded?.symptoms ?? []))
  const [draft, setDraft] = useState(loaded?.narrative ?? "")
  const [unknown, setUnknown] = useState<string[]>([])
  const [parseNote, setParseNote] = useState("")
  const [openExam, setOpenExam] = useState<Exam | "none">("inspection")
  const [query, setQuery] = useState("")
  const [activeId, setActiveId] = useState<string | null>(loaded?.primary ?? null)

  const symptomList = useMemo(() => Array.from(selected), [selected])
  const analysis = useMemo(() => analyze(symptomList, domain), [symptomList, domain])
  const neighbors = useMemo(() => neighborReading(symptomList, domain), [symptomList, domain])
  const related = useMemo(() => (domain === "holistic" ? relatedDiseases(symptomList) : []), [domain, symptomList])

  function toggle(id: string) {
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
    setAnalyzed(false)
    setActiveId(null)
    if (step === 3) setStep(2)
  }

  function parseDraft() {
    const parsed = parseSymptomText(draft)
    if (parsed.ids.length === 0) {
      setParseNote("None of that text matched the symptom dictionary.")
      setUnknown(parsed.unrecognized)
      return
    }
    setSelected((current) => new Set([...current, ...parsed.ids]))
    setUnknown(parsed.unrecognized)
    setParseNote(`Added ${parsed.ids.length} symptom${parsed.ids.length === 1 ? "" : "s"} from the description.`)
    setAnalyzed(false)
    setStep(2)
  }

  function clearChart() {
    setSelected(new Set())
    setDraft("")
    setUnknown([])
    setParseNote("")
    setActiveId(null)
    setAnalyzed(false)
    setStep(1)
    router.replace("/explorer", { scroll: false })
  }

  function loadCase(id: string) {
    router.replace(`/explorer?case=${id}`, { scroll: false })
  }

  function runAnalyze() {
    if (selected.size === 0) return
    setAnalyzed(true)
    setStep(3)
    setActiveId(null)
  }

  const filteredByExam = (exam: Exam) =>
    symptoms.filter((item) => {
      if (item.exam !== exam) return false
      if (!query.trim()) return true
      const needle = query.trim().toLowerCase()
      return (
        item.name.toLowerCase().includes(needle) ||
        item.chinese.includes(query.trim()) ||
        item.aliases.some((alias) => alias.includes(needle)) ||
        item.field.toLowerCase().includes(needle)
      )
    })

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.16em] text-primary uppercase">Syndrome Explorer</p>
          <h1 className="font-heading mt-1 text-2xl tracking-tight text-ink sm:text-3xl">
            Four examinations · teaching demonstration
          </h1>
        </div>
        <div className="flex gap-1 rounded-md border border-wood/35 bg-card p-1">
          <Button
            type="button"
            size="sm"
            variant={panel === "chart" ? "default" : "ghost"}
            onClick={() => setPanel("chart")}
          >
            Chart
          </Button>
          <Button
            type="button"
            size="sm"
            variant={panel === "atlas" ? "default" : "ghost"}
            onClick={() => setPanel("atlas")}
          >
            Pattern atlas
          </Button>
        </div>
      </div>

      {panel === "atlas" ? (
        <div className="-mx-4">
          <AtlasView />
        </div>
      ) : (
        <>
          <div className="mb-6 rounded-md border border-cinnabar/30 bg-[color-mix(in_srgb,var(--cinnabar)_6%,var(--warm-white))] px-4 py-3 text-sm leading-relaxed text-foreground">
            <span className="font-medium text-cinnabar">Educational teaching-pattern demonstration. </span>
            Pattern-coverage scores come from the rule-based teaching engine. They are{" "}
            <strong>not</strong> clinical probabilities and <strong>not</strong> outputs from the trained TCM-SD
            machine-learning models.
          </div>

          <StepRail step={step} />

          <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
            <section className="space-y-5">
              <div className="rounded-xl border border-wood/30 bg-card p-4">
                <h2 className="font-heading text-lg text-ink">
                  <span className="mr-2 text-sm text-primary">Step 1</span>
                  Enter symptoms
                </h2>

                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  {domains.map((item) => (
                    <Button
                      key={item}
                      type="button"
                      variant={domain === item ? "default" : "outline"}
                      className="h-auto justify-start px-3 py-2 text-left whitespace-normal"
                      onClick={() => {
                        setDomain(item)
                        setAnalyzed(false)
                        if (step === 3) setStep(2)
                      }}
                    >
                      <span>
                        <span className="block text-sm">{DOMAIN_META[item].label}</span>
                        <span
                          className={cn(
                            "font-cjk block text-xs",
                            domain === item ? "text-primary-foreground/80" : "text-muted-foreground",
                          )}
                        >
                          {DOMAIN_META[item].chinese}
                        </span>
                      </span>
                    </Button>
                  ))}
                </div>

                <div className="mt-4 space-y-2">
                  <label className="sr-only" htmlFor="sample-chart">
                    Load a sample teaching case
                  </label>
                  <select
                    id="sample-chart"
                    className="border-input bg-background h-9 w-full rounded-md border px-3 text-sm sm:max-w-md"
                    value={loaded?.id ?? ""}
                    onChange={(event) => {
                      const next = event.target.value
                      if (!next) {
                        clearChart()
                        return
                      }
                      loadCase(next)
                    }}
                  >
                    <option value="">Load a sample teaching case</option>
                    {showcaseCases.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.title}
                      </option>
                    ))}
                  </select>
                  {missingCase && <p className="text-sm text-destructive">That sample chart is not in the library.</p>}
                  <Textarea
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    placeholder="Describe the chart: cold hands, sore lower back, greasy coat, deep weak pulse…"
                    rows={3}
                  />
                  <div className="flex flex-wrap gap-2">
                    <Button type="button" variant="outline" onClick={parseDraft}>
                      Parse description
                    </Button>
                    <Button type="button" variant="ghost" onClick={clearChart}>
                      Clear
                    </Button>
                    <span className="self-center text-xs text-muted-foreground">{selected.size} selected</span>
                  </div>
                  {parseNote && <p className="text-sm">{parseNote}</p>}
                  {unknown.length > 0 && (
                    <p className="text-sm text-muted-foreground">Unrecognized: {unknown.join(", ")}</p>
                  )}
                </div>

                <div className="mt-4 space-y-2">
                  <Input
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Search symptoms"
                    className="sm:max-w-xs"
                  />
                  {exams.map((exam) => {
                    const items = filteredByExam(exam)
                    const open = openExam === exam
                    return (
                      <div key={exam} className="overflow-hidden rounded-md border border-wood/25">
                        <button
                          type="button"
                          className="flex w-full items-center justify-between bg-secondary/60 px-3 py-2 text-left text-sm"
                          onClick={() => setOpenExam(open ? "none" : exam)}
                        >
                          <span>
                            {EXAM_LABEL[exam]}{" "}
                            <span className="font-cjk text-muted-foreground">{EXAM_CHINESE[exam]}</span>
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {items.filter((s) => selected.has(s.id)).length}/{items.length} · {open ? "Hide" : "Show"}
                          </span>
                        </button>
                        {open && (
                          <div className="flex flex-wrap gap-1.5 p-3">
                            {items.length === 0 && (
                              <p className="text-sm text-muted-foreground">No matches in this examination.</p>
                            )}
                            {items.map((item) => {
                              const on = selected.has(item.id)
                              return (
                                <Button
                                  key={item.id}
                                  type="button"
                                  size="sm"
                                  variant={on ? "default" : "outline"}
                                  aria-pressed={on}
                                  className="h-auto py-1 whitespace-normal"
                                  onClick={() => toggle(item.id)}
                                >
                                  {item.name}
                                  <span
                                    className={cn(
                                      "font-cjk",
                                      on ? "text-primary-foreground/80" : "text-muted-foreground",
                                    )}
                                  >
                                    {item.chinese}
                                  </span>
                                </Button>
                              )
                            })}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="rounded-xl border border-wood/30 bg-card p-4">
                <h2 className="font-heading text-lg text-ink">
                  <span className="mr-2 text-sm text-primary">Step 2</span>
                  Analyze
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Run the teaching-pattern engine on the current chart. Scoring is unchanged from the existing desk.
                </p>
                <Button
                  type="button"
                  size="lg"
                  className="mt-4 rounded-md"
                  disabled={selected.size === 0}
                  onClick={runAnalyze}
                >
                  Analyze Symptoms
                </Button>
              </div>
            </section>

            <aside className="lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:overflow-auto">
              <div className="mb-3">
                <h2 className="font-heading text-lg text-ink">
                  <span className="mr-2 text-sm text-primary">Step 3</span>
                  Explore results
                </h2>
              </div>
              {!analyzed || selected.size === 0 ? (
                <div className="rounded-xl border border-dashed border-wood/40 bg-card p-5 text-sm leading-relaxed text-muted-foreground">
                  Select symptoms (or load a sample case), then press <em>Analyze Symptoms</em> to see leading patterns,
                  matched signs, and missing evidence.
                </div>
              ) : (
                <ResultPanel
                  analysis={analysis}
                  domain={domain}
                  activeId={activeId}
                  onActive={(id) => setActiveId((current) => (current === id ? null : id))}
                  neighbors={neighbors}
                  related={related}
                />
              )}
            </aside>
          </div>
        </>
      )}
    </div>
  )
}

function StepRail({ step }: { step: 1 | 2 | 3 }) {
  const items = [
    { n: 1 as const, label: "Enter symptoms" },
    { n: 2 as const, label: "Analyze" },
    { n: 3 as const, label: "Explore results" },
  ]
  return (
    <ol className="flex flex-wrap gap-2">
      {items.map((item) => (
        <li
          key={item.n}
          className={cn(
            "flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm",
            step === item.n
              ? "border-primary bg-primary text-primary-foreground"
              : step > item.n
                ? "border-primary/40 bg-accent text-foreground"
                : "border-wood/30 bg-card text-muted-foreground",
          )}
        >
          <span className="font-medium">{item.n}</span>
          {item.label}
        </li>
      ))}
    </ol>
  )
}
