"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { showcaseCases } from "@/lib/cases"
import { analyze } from "@/lib/engine"
import { symptomById } from "@/lib/symptoms"
import { DOMAIN_META, syndromeById } from "@/lib/syndromes"
import type { Domain } from "@/lib/types"

const filters: Array<Domain | "all"> = ["all", "holistic", "kidney", "stomach", "dysmenorrhea"]

export function CaseLibrary() {
  const [filter, setFilter] = useState<Domain | "all">("all")
  const cases = showcaseCases.filter((item) => filter === "all" || item.domain === filter)

  const readings = useMemo(
    () =>
      showcaseCases.map((item) => {
        const analysis = analyze(item.symptoms, item.domain)
        const layer = syndromeById.get(item.primary)?.layer
        const ranked = analysis.ranked.filter((row) => syndromeById.get(row.id)?.layer === layer)
        const primary = analysis.ranked.find((row) => row.id === item.primary)
        return {
          id: item.id,
          agrees: ranked.slice(0, 3).some((row) => row.id === item.primary),
          score: primary?.score ?? 0,
          top: ranked[0]?.id,
        }
      }),
    [],
  )
  const byId = new Map(readings.map((item) => [item.id, item]))

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-6">
      <div>
        <p className="text-xs tracking-[0.18em] text-primary uppercase">Sample charts</p>
        <h1 className="font-heading mt-1 text-3xl tracking-tight">Teaching cases, not clinical records</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Each chart was written so a known pattern should lead. Open one to see the multi-label reading, including the organ and principle tags that travel with it.
        </p>
      </div>
      <div className="flex flex-wrap gap-2">
        {filters.map((item) => (
          <Button key={item} type="button" size="sm" variant={filter === item ? "default" : "outline"} onClick={() => setFilter(item)}>
            {item === "all" ? "All lenses" : DOMAIN_META[item].label}
          </Button>
        ))}
      </div>
      {cases.length === 0 && <p className="text-sm text-muted-foreground">No sample charts in this lens.</p>}
      <div className="grid gap-4 md:grid-cols-2">
        {cases.map((item) => {
          const reading = byId.get(item.id)
          const primary = syndromeById.get(item.primary)
          return (
            <Card key={item.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <CardTitle className="font-heading text-lg">{item.title}</CardTitle>
                  <Badge variant={reading?.agrees ? "secondary" : "destructive"}>{reading?.agrees ? "Leads" : "Check"}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {DOMAIN_META[item.domain].label} · {primary?.name}{" "}
                  <span className="font-cjk">{primary?.chinese}</span>
                </p>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <p className="leading-relaxed text-muted-foreground">{item.narrative}</p>
                <p>{item.note}</p>
                <p className="text-xs text-muted-foreground">
                  {item.symptoms.length} signs, including {item.symptoms.slice(0, 4).map((id) => symptomById.get(id)?.name).join(", ")}.
                  {reading ? ` Pattern coverage ${Math.round(reading.score * 100)}.` : ""}
                </p>
                <Button asChild>
                  <Link href={`/?case=${item.id}`}>Open on the chart</Link>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
