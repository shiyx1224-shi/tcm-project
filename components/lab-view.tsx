"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { labReport } from "@/lib/engine"
import { symptomById } from "@/lib/symptoms"

export function LabView() {
  const report = useMemo(() => labReport(), [])
  const [ranker, baseline, neighbors] = report.rows

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-6">
      <div>
        <p className="text-xs tracking-[0.18em] text-primary uppercase">Teaching lab</p>
        <h1 className="font-heading mt-1 text-3xl tracking-tight">How the readers behave when signs go missing</h1>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">
          {report.cases} charts: the sample narratives, plus synthetic charts grown from the same pattern profiles with dropped signs, a companion pattern, and an occasional distractor.
          These numbers describe recovery on that teaching set. They are not the clinical results in Gong, Huang, or Chen, and the neighbor method has an advantage because it memorizes charts built from the same profiles.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Multi-label metrics</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full min-w-[40rem] text-left text-sm">
            <thead className="text-xs tracking-wide text-muted-foreground uppercase">
              <tr>
                <th className="py-2 pr-3 font-medium">Reader</th>
                <th className="py-2 pr-3 font-medium">Example F1</th>
                <th className="py-2 pr-3 font-medium">Hamming loss</th>
                <th className="py-2 pr-3 font-medium">Average precision</th>
                <th className="py-2 pr-3 font-medium">One-error</th>
                <th className="py-2 font-medium">Exact match</th>
              </tr>
            </thead>
            <tbody>
              {report.rows.map((row) => (
                <tr key={row.model} className="border-t">
                  <td className="py-3 pr-3 font-medium">{row.model}</td>
                  <td className="py-3 pr-3">{row.exampleF1.toFixed(3)}</td>
                  <td className="py-3 pr-3">{row.hamming.toFixed(3)}</td>
                  <td className="py-3 pr-3">{row.averagePrecision.toFixed(3)}</td>
                  <td className="py-3 pr-3">{row.oneError.toFixed(3)}</td>
                  <td className="py-3">{row.subsetAccuracy.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4 space-y-2 text-sm leading-relaxed text-muted-foreground">
            <p>
              The pattern ranker reaches an example F1 of {ranker.exampleF1.toFixed(3)}, against {baseline.exampleF1.toFixed(3)} for an unweighted overlap baseline and {neighbors.exampleF1.toFixed(3)} for leave-one-out ML-KNN.
              Hamming loss stays small because most syndrome labels are correctly absent, the same wide-label effect that makes Hamming look optimistic in multi-syndrome papers.
            </p>
            <p>
              Example F1 asks whether the set of labels above the line matches the set that should be there. Average precision asks whether the true labels sit near the top of the ranking. One-error asks only whether the single top label is wrong. Exact match is harsh: every extra or missing label fails the chart.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Discriminative symptoms</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              A multi-label Relief-style weight. A symptom scores higher when charts with different syndrome sets disagree on it, and lower when charts with similar syndrome sets disagree on it. This is the feature-ranking idea, shown rather than folded silently into the live score.
            </p>
            <ul className="space-y-2">
              {report.relief.map((item) => {
                const symptom = symptomById.get(item.id)
                return (
                  <li key={item.id}>
                    <div className="mb-1 flex justify-between gap-3">
                      <span>
                        {symptom?.name} <span className="font-cjk text-muted-foreground">{symptom?.chinese}</span>
                      </span>
                      <span className="text-xs text-muted-foreground">{item.weight.toFixed(2)}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted">
                      <div className="h-full rounded-full bg-chart-2" style={{ width: `${Math.round(item.weight * 100)}%` }} />
                    </div>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>What each reader is doing</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-relaxed text-muted-foreground">
            <p>
              <span className="text-foreground">Pattern ranker.</span> Weighted key signs, a penalty for contradicting signs, a small boost when a known cross-feature is present, and a soft contest inside exterior/interior, cold/heat, and deficiency/excess.
            </p>
            <p>
              <span className="text-foreground">Overlap baseline.</span> The share of a pattern&apos;s signs that appear, with no weights, no contradictions, and no competing pairs. This is the ablation: structure should beat raw overlap on example F1.
            </p>
            <p>
              <span className="text-foreground">ML-KNN.</span> Five nearest teaching charts by symptom Hamming distance, with a smoothed vote for each label. Gong and Huang both use it as a classical multi-label comparison. Here it is leave-one-out on the teaching set only.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
