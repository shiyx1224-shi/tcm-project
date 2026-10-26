"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Analysis, Domain, RankedSyndrome } from "@/lib/types"
import { symptomById } from "@/lib/symptoms"
import { DOMAIN_META, syndromeById } from "@/lib/syndromes"
import { cn } from "@/lib/utils"

const layerTitle = {
  disease: "Disease patterns",
  pathology: "Pathology",
  principle: "Eight principles",
  organ: "Organ location",
} as const

export function ResultPanel({
  analysis,
  domain,
  activeId,
  onActive,
  neighbors,
  related,
}: {
  analysis: Analysis
  domain: Domain
  activeId: string | null
  onActive: (id: string) => void
  neighbors: { id: string; score: number }[]
  related: RankedSyndrome[]
}) {
  if (analysis.symptomCount === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-xl">The chart is empty</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-relaxed text-muted-foreground">
          <p>
            Choose symptoms from the four examinations, or paste a short description and parse it.
            A sample chart is the fastest way to see a multi-label reading.
          </p>
          <p>Nothing is inferred until at least one sign is on the chart.</p>
        </CardContent>
      </Card>
    )
  }

  const allowed = new Set(
    analysis.ranked
      .map((row) => syndromeById.get(row.id))
      .filter((syndrome) => syndrome && (syndrome.layer !== "disease" || syndrome.domains.includes(domain)))
      .map((syndrome) => syndrome!.id),
  )
  const visible = analysis.ranked.filter((row) => allowed.has(row.id) && row.band !== "low")
  const groups = ["disease", "pathology", "principle", "organ"] as const
  const ordered = domain === "holistic" ? (["principle", "organ", "pathology"] as const) : groups
  const above = visible.length
  const filledExams = analysis.exams.filter((exam) => exam.count > 0).length

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-xl">
            {above === 0 ? "No pattern clears the line" : `${above} labels are on the chart`}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-relaxed">
          <p>
            {DOMAIN_META[domain].label} lens. {DOMAIN_META[domain].blurb}
          </p>
          <p className="text-muted-foreground">
            {above > 1
              ? "These labels are allowed to co-exist. The desk does not force the chart into a single class."
              : above === 1
                ? "One label is leading. Competing signs would split the reading into more than one pattern."
                : "The closest patterns are incomplete. Tongue, pulse, or a sharper pain description usually moves the chart."}
          </p>
          <div className="grid grid-cols-4 gap-2">
            {analysis.exams.map((exam) => (
              <div key={exam.exam} className="rounded-lg border bg-background px-2 py-2">
                <div className="text-[11px] tracking-wide text-muted-foreground uppercase">{exam.label.split(" ")[0]}</div>
                <div className="font-heading text-lg">{exam.count}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            {filledExams} of 4 examinations are filled, across {analysis.fieldsFilled} of {analysis.fieldTotal} symptom fields.
            {analysis.missingTongue ? " Tongue is empty." : " Tongue is recorded."}
            {analysis.missingPulse ? " Pulse is empty." : " Pulse is recorded."}
            {analysis.missingTongue && analysis.missingPulse ? " Coverage is slightly discounted until one of those is added." : ""}
          </p>
        </CardContent>
      </Card>

      {above === 0 && (
        <div className="space-y-2">
          {analysis.ranked.slice(0, 3).map((row) => (
            <PatternCard key={row.id} row={row} open={activeId === row.id} onActive={onActive} />
          ))}
        </div>
      )}

      {ordered.map((layer) => {
        const rows = visible.filter((row) => syndromeById.get(row.id)?.layer === layer)
        if (rows.length === 0) return null
        return (
          <section key={layer} className="space-y-2">
            <h2 className="font-heading text-sm tracking-wide text-muted-foreground uppercase">{layerTitle[layer]}</h2>
            {rows.map((row) => (
              <PatternCard key={row.id} row={row} open={activeId === row.id} onActive={onActive} />
            ))}
          </section>
        )
      })}

      {domain === "holistic" && related.length > 0 && (
        <section className="space-y-2">
          <h2 className="font-heading text-sm tracking-wide text-muted-foreground uppercase">Disease patterns that also fit</h2>
          <p className="text-xs text-muted-foreground">Switch the lens if you want these judged inside a kidney, stomach, or menstrual catalog.</p>
          {related.map((row) => (
            <PatternCard key={row.id} row={row} open={activeId === row.id} onActive={onActive} />
          ))}
        </section>
      )}

      {analysis.constraints.length > 0 && (
        <Card size="sm">
          <CardHeader>
            <CardTitle>Competing pairs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {analysis.constraints.map((note) => (
              <p key={note.group}>{note.note}</p>
            ))}
          </CardContent>
        </Card>
      )}

      {analysis.crossHits.length > 0 && (
        <Card size="sm">
          <CardHeader>
            <CardTitle>Cross features</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {analysis.crossHits.map((hit) => (
              <div key={hit.id}>
                <p className="font-medium">{hit.name}</p>
                <p className="text-muted-foreground">{hit.note}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {neighbors.length > 0 && (
        <Card size="sm">
          <CardHeader>
            <CardTitle>Neighbor reading</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="text-muted-foreground">
              ML-KNN style votes from the five nearest teaching charts in this lens. This memorizes the teaching set. It is not a clinical cohort.
            </p>
            <ul className="space-y-1">
              {neighbors.map((row) => {
                const syndrome = syndromeById.get(row.id)
                if (!syndrome) return null
                return (
                  <li key={row.id} className="flex items-baseline justify-between gap-3">
                    <span>
                      {syndrome.name} <span className="font-cjk text-muted-foreground">{syndrome.chinese}</span>
                    </span>
                    <span className="text-xs text-muted-foreground">{Math.round(row.score * 5)}/5 neighbors</span>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function PatternCard({
  row,
  open,
  onActive,
}: {
  row: RankedSyndrome
  open: boolean
  onActive: (id: string) => void
}) {
  const syndrome = syndromeById.get(row.id)
  if (!syndrome) return null
  const percent = Math.round(row.score * 100)

  return (
    <Card size="sm" className={cn(row.band === "consider" && "opacity-90")}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="font-heading text-base">
              {syndrome.name} <span className="font-cjk font-normal text-muted-foreground">{syndrome.chinese}</span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">{syndrome.pinyin}</p>
          </div>
          <Badge variant={row.band === "suggested" ? "default" : "secondary"}>
            {row.band === "suggested" ? "Suggested" : "Consider"} · {percent}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <div className="h-full rounded-full bg-primary" style={{ width: `${percent}%` }} />
        </div>
        <p className="text-sm text-muted-foreground">{syndrome.summary}</p>
        <button type="button" className="text-sm font-medium text-primary underline-offset-4 hover:underline" onClick={() => onActive(row.id)}>
          {open ? "Hide the evidence" : "Show which signs carried it"}
        </button>
        {open && (
          <div className="space-y-2 border-t pt-3 text-sm">
            <p>{syndrome.reading}</p>
            <Evidence label="On the chart" ids={[...row.matchedKey, ...row.matchedSupport]} />
            <Evidence label="Key signs still missing" ids={row.missingKey} />
            <Evidence label="Signs that argue against it" ids={row.againstHits} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function Evidence({ label, ids }: { label: string; ids: string[] }) {
  if (ids.length === 0) return null
  return (
    <p>
      <span className="text-muted-foreground">{label}: </span>
      {ids.map((id) => symptomById.get(id)?.name ?? id).join(", ")}
    </p>
  )
}
