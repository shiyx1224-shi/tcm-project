"use client"

import { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { ResultPanel } from "@/components/result-panel"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { showcaseCases } from "@/lib/cases"
import { analyze, neighborReading, relatedDiseases } from "@/lib/engine"
import { EXAM_CHINESE, EXAM_LABEL, parseSymptomText, symptoms } from "@/lib/symptoms"
import { DOMAIN_META } from "@/lib/syndromes"
import type { Domain, Exam } from "@/lib/types"
import { cn } from "@/lib/utils"

const domains: Domain[] = ["holistic", "kidney", "stomach", "dysmenorrhea"]
const exams: Array<Exam | "all"> = ["all", "inspection", "listening", "inquiry", "palpation"]

export function ConsultDesk({ initialCaseId }: { initialCaseId: string | null }) {
  const router = useRouter()
  const loaded = showcaseCases.find((entry) => entry.id === initialCaseId) ?? null
  const missingCase = Boolean(initialCaseId && !loaded)
  const [domain, setDomain] = useState<Domain>(loaded?.domain ?? "holistic")
  const [selected, setSelected] = useState<Set<string>>(new Set(loaded?.symptoms ?? []))
  const [draft, setDraft] = useState(loaded?.narrative ?? "")
  const [unknown, setUnknown] = useState<string[]>([])
  const [parseNote, setParseNote] = useState("")
  const [exam, setExam] = useState<Exam | "all">("all")
  const [query, setQuery] = useState("")
  const [activeId, setActiveId] = useState<string | null>(loaded?.primary ?? null)

  const symptomList = useMemo(() => Array.from(selected), [selected])
  const analysis = useMemo(() => analyze(symptomList, domain), [symptomList, domain])
  const neighbors = useMemo(() => neighborReading(symptomList, domain), [symptomList, domain])
  const related = useMemo(() => (domain === "holistic" ? relatedDiseases(symptomList) : []), [domain, symptomList])

  const visibleSymptoms = symptoms.filter((item) => {
    if (exam !== "all" && item.exam !== exam) return false
    if (!query.trim()) return true
    const needle = query.trim().toLowerCase()
    return (
      item.name.toLowerCase().includes(needle) ||
      item.chinese.includes(query.trim()) ||
      item.aliases.some((alias) => alias.includes(needle)) ||
      item.field.toLowerCase().includes(needle)
    )
  })

  function toggle(id: string) {
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
    setActiveId(null)
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
  }

  function clearChart() {
    setSelected(new Set())
    setDraft("")
    setUnknown([])
    setParseNote("")
    setActiveId(null)
    router.replace("/", { scroll: false })
  }

  function loadCase(id: string) {
    router.replace(`/?case=${id}`, { scroll: false })
  }

  const fields = groupFields(visibleSymptoms)

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-6 lg:grid-cols-[minmax(0,1fr)_22.5rem]">
      <section className="space-y-5">
        <div>
          <p className="text-xs tracking-[0.18em] text-primary uppercase">Syndrome differentiation</p>
          <h1 className="font-heading mt-1 text-3xl tracking-tight sm:text-4xl">Chart a case across the four examinations</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            Symptoms are standardized, then read as a multi-label pattern. Exterior competes with interior, cold with heat, and deficiency with excess. More than one pattern can remain.
          </p>
        </div>

        <div className="grid gap-2 sm:grid-cols-2">
          {domains.map((item) => (
            <Button
              key={item}
              type="button"
              variant={domain === item ? "default" : "outline"}
              className="h-auto justify-start px-3 py-2 text-left whitespace-normal"
              onClick={() => setDomain(item)}
            >
              <span>
                <span className="block text-sm">{DOMAIN_META[item].label}</span>
                <span className={cn("font-cjk block text-xs", domain === item ? "text-primary-foreground/80" : "text-muted-foreground")}>
                  {DOMAIN_META[item].chinese}
                </span>
              </span>
            </Button>
          ))}
        </div>

        <div className="space-y-2 rounded-xl border bg-card p-3">
          <div className="flex flex-col gap-2 sm:flex-row">
              <Select value={loaded?.id} onValueChange={loadCase}>
              <SelectTrigger className="w-full sm:max-w-xs">
                <SelectValue placeholder="Load a sample chart" />
              </SelectTrigger>
              <SelectContent>
                {showcaseCases.map((item) => (
                  <SelectItem key={item.id} value={item.id}>
                    {item.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs leading-relaxed text-muted-foreground">
              Sample charts are written for teaching. They are not records from the parent studies.
            </p>
          </div>
          {missingCase && <p className="text-sm text-destructive">That sample chart is not in the library.</p>}
          <Textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Describe the chart in ordinary words: cold hands and feet, sore lower back, swollen ankles, greasy coat, deep weak pulse…"
            rows={4}
          />
          <div className="flex flex-wrap gap-2">
            <Button type="button" onClick={parseDraft}>
              Parse description
            </Button>
            <Button type="button" variant="outline" onClick={clearChart}>
              Clear chart
            </Button>
            <span className="self-center text-xs text-muted-foreground">{selected.size} symptoms selected</span>
          </div>
          {parseNote && <p className="text-sm">{parseNote}</p>}
          {unknown.length > 0 && (
            <p className="text-sm text-muted-foreground">
              Unrecognized words: {unknown.join(", ")}. Try a dictionary phrase such as pale tongue, wiry pulse, or night sweats.
            </p>
          )}
        </div>

        <div className="space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div className="flex gap-1 overflow-x-auto">
              {exams.map((item) => (
                <Button key={item} type="button" size="sm" variant={exam === item ? "default" : "outline"} onClick={() => setExam(item)}>
                  {item === "all" ? "All four" : EXAM_LABEL[item]}
                  {item !== "all" && <span className="font-cjk">{EXAM_CHINESE[item]}</span>}
                </Button>
              ))}
            </div>
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search symptoms"
              className="sm:max-w-xs"
            />
          </div>

          {fields.length === 0 && (
            <p className="rounded-lg border border-dashed px-3 py-6 text-sm text-muted-foreground">
              No symptoms match that search in this examination.
            </p>
          )}

          {fields.map(([field, items]) => (
            <div key={field}>
              <h2 className="mb-2 text-xs tracking-wide text-muted-foreground uppercase">{field}</h2>
              <div className="flex flex-wrap gap-2">
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
                      <span className={cn("font-cjk", on ? "text-primary-foreground/80" : "text-muted-foreground")}>{item.chinese}</span>
                    </Button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </section>

      <aside className="lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:overflow-auto lg:pr-1">
        <ResultPanel
          analysis={analysis}
          domain={domain}
          activeId={activeId}
          onActive={(id) => setActiveId((current) => (current === id ? null : id))}
          neighbors={neighbors}
          related={related}
        />
      </aside>
    </div>
  )
}

function groupFields(items: typeof symptoms) {
  const groups = new Map<string, typeof symptoms>()
  for (const item of items) {
    const list = groups.get(item.field) ?? []
    list.push(item)
    groups.set(item.field, list)
  }
  return Array.from(groups.entries())
}
