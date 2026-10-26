"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cooccurrence } from "@/lib/engine"
import { symptomById } from "@/lib/symptoms"
import { syndromeById, syndromes } from "@/lib/syndromes"
import { cn } from "@/lib/utils"

const layerLabel = {
  principle: "Principle",
  organ: "Organ",
  pathology: "Pathology",
  disease: "Disease",
} as const

export function AtlasView() {
  const [query, setQuery] = useState("")
  const [activeId, setActiveId] = useState(syndromes[0]?.id ?? "")
  const filtered = syndromes.filter((item) => {
    const needle = query.trim().toLowerCase()
    if (!needle) return true
    return (
      item.name.toLowerCase().includes(needle) ||
      item.chinese.includes(query.trim()) ||
      item.pinyin.toLowerCase().includes(needle) ||
      item.summary.toLowerCase().includes(needle)
    )
  })
  const active = syndromeById.get(activeId) ?? filtered[0]
  const matrix = active ? cooccurrence(active.id) : null

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-6 lg:grid-cols-[18rem_minmax(0,1fr)]">
      <div className="space-y-3">
        <div>
          <p className="text-xs tracking-[0.18em] text-primary uppercase">Pattern atlas</p>
          <h1 className="font-heading mt-1 text-3xl tracking-tight">What each pattern is watching for</h1>
        </div>
        <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search patterns" />
        <div className="max-h-[70vh] space-y-1 overflow-auto pr-1">
          {filtered.length === 0 && <p className="text-sm text-muted-foreground">No pattern uses that name.</p>}
          {filtered.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveId(item.id)}
              className={cn(
                "w-full rounded-lg border px-3 py-2 text-left",
                active?.id === item.id ? "border-primary bg-primary text-primary-foreground" : "bg-card hover:bg-secondary",
              )}
            >
              <span className="block text-sm">{item.name}</span>
              <span className={cn("font-cjk text-xs", active?.id === item.id ? "text-primary-foreground/80" : "text-muted-foreground")}>
                {item.chinese}
              </span>
            </button>
          ))}
        </div>
      </div>

      {active && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">{layerLabel[active.layer]}</Badge>
                {active.constraint && <Badge variant="secondary">Competes as {active.pole}</Badge>}
              </div>
              <CardTitle className="font-heading text-3xl">
                {active.name} <span className="font-cjk text-muted-foreground">{active.chinese}</span>
              </CardTitle>
              <p className="text-sm text-muted-foreground">{active.pinyin}</p>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-relaxed">
              <p>{active.summary}</p>
              <p className="text-muted-foreground">{active.reading}</p>
              <SymptomLine label="Key signs" ids={active.key.map((item) => item.id)} />
              <SymptomLine label="Supporting signs" ids={active.support.map((item) => item.id)} />
              <SymptomLine label="Argues against" ids={active.against} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>How the key signs travel together</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p className="text-muted-foreground">
                Each cell is the share of teaching charts labeled with this pattern that contain both signs. The set is synthetic plus the sample charts, so the matrix shows the profile, not a hospital co-occurrence study.
              </p>
              {matrix && matrix.cases > 0 && matrix.symptoms.length > 0 ? (
                <div className="overflow-x-auto">
                  <p className="mb-2 text-xs text-muted-foreground">{matrix.cases} teaching charts carry this label.</p>
                  <div
                    className="grid gap-1"
                    style={{ gridTemplateColumns: `7rem repeat(${matrix.symptoms.length}, minmax(2.4rem, 1fr))` }}
                  >
                    <span />
                    {matrix.symptoms.map((id) => (
                      <span key={id} className="truncate text-[10px] text-muted-foreground" title={symptomById.get(id)?.name}>
                        {symptomById.get(id)?.name}
                      </span>
                    ))}
                    {matrix.symptoms.map((rowId, row) => (
                      <FragmentRow key={rowId} label={symptomById.get(rowId)?.name ?? rowId} values={matrix.matrix[row]} />
                    ))}
                  </div>
                </div>
              ) : (
                <p>Not enough teaching charts mention this pattern yet.</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function SymptomLine({ label, ids }: { label: string; ids: string[] }) {
  if (ids.length === 0) return null
  return (
    <p>
      <span className="text-muted-foreground">{label}: </span>
      {ids.map((id) => symptomById.get(id)?.name ?? id).join(", ")}
    </p>
  )
}

function FragmentRow({ label, values }: { label: string; values: number[] }) {
  return (
    <>
      <span className="truncate text-[10px] text-muted-foreground" title={label}>
        {label}
      </span>
      {values.map((value, index) => (
        <span
          key={`${label}-${index}`}
          className="grid h-8 place-items-center rounded-sm text-[10px]"
          style={{ backgroundColor: `oklch(0.46 0.14 30 / ${0.08 + value * 0.85})`, color: value > 0.65 ? "white" : "inherit" }}
        >
          {Math.round(value * 100)}
        </span>
      ))}
    </>
  )
}
