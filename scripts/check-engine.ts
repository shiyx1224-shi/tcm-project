import { showcaseCases } from "../lib/cases"
import { crossFeatures } from "../lib/cross-features"
import { analyze, labReport } from "../lib/engine"
import { symptomById } from "../lib/symptoms"
import { syndromeById, syndromes } from "../lib/syndromes"

const missing = new Set<string>()

function watch(id: string, source: string) {
  if (!symptomById.has(id)) missing.add(`${source}: ${id}`)
}

for (const syndrome of syndromes) {
  if (syndromeById.get(syndrome.id) !== syndrome) throw new Error(`duplicate ${syndrome.id}`)
  for (const item of [...syndrome.key, ...syndrome.support]) watch(item.id, syndrome.id)
  for (const id of syndrome.against) watch(id, `${syndrome.id} against`)
  for (const id of syndrome.companions) {
    if (!syndromeById.has(id)) missing.add(`${syndrome.id} companion ${id}`)
  }
  for (const id of syndrome.implies) {
    if (!syndromeById.has(id)) missing.add(`${syndrome.id} implies ${id}`)
  }
}
for (const feature of crossFeatures) {
  for (const id of feature.symptoms) watch(id, feature.id)
  for (const id of feature.boosts) {
    if (!syndromeById.has(id)) missing.add(`${feature.id} boost ${id}`)
  }
}
for (const item of showcaseCases) {
  if (!syndromeById.has(item.primary)) missing.add(`case ${item.id} primary`)
  for (const id of item.symptoms) watch(id, item.id)
}

if (missing.size > 0) {
  console.error("Missing references:")
  for (const item of missing) console.error(" -", item)
  process.exit(1)
}

let failed = 0
for (const item of showcaseCases) {
  const analysis = analyze(item.symptoms, item.domain)
  const layer = syndromeById.get(item.primary)!.layer
  const inLayer = analysis.ranked.filter((row) => syndromeById.get(row.id)?.layer === layer)
  const top = inLayer.slice(0, 3)
  const found = top.some((row) => row.id === item.primary)
  const primary = analysis.ranked.find((row) => row.id === item.primary)
  const ok = found && (primary?.score ?? 0) >= 0.46
  if (!ok) {
    failed += 1
    console.log(`FAIL ${item.id} primary=${item.primary} score=${primary?.score.toFixed(3)} band=${primary?.band}`)
    console.log(
      "  top layer:",
      top.map((row) => `${row.id}:${row.score.toFixed(2)}`).join(", "),
    )
    console.log(
      "  top all:",
      analysis.ranked.slice(0, 8).map((row) => `${row.id}:${row.score.toFixed(2)}`).join(", "),
    )
  } else {
    console.log(`ok   ${item.id} ${item.primary} ${primary?.score.toFixed(2)} via ${top.map((row) => row.id).join(" > ")}`)
  }
}

const report = labReport()
console.log(`\nTeaching cases: ${report.cases}`)
for (const row of report.rows) {
  console.log(
    `${row.model}: F1 ${row.exampleF1.toFixed(3)}  Hamming ${row.hamming.toFixed(3)}  AP ${row.averagePrecision.toFixed(3)}  one-error ${row.oneError.toFixed(3)}  subset ${row.subsetAccuracy.toFixed(3)}`,
  )
}
console.log("Relief leaders:", report.relief.slice(0, 8).map((item) => item.id).join(", "))

if (failed > 0) process.exit(1)
