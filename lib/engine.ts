import { showcaseCases } from "./cases"
import { crossFeatures } from "./cross-features"
import { EXAM_LABEL, PULSE_FIELDS, symptomById, symptoms, TONGUE_FIELDS } from "./symptoms"
import { catalogFor, syndromeById, syndromes } from "./syndromes"
import type {
  Analysis,
  Band,
  ConstraintNote,
  Domain,
  RankedSyndrome,
  Syndrome,
  TeachingCase,
} from "./types"

export const SUGGEST_AT = 0.62
export const CONSIDER_AT = 0.46

const EXAMS = ["inspection", "listening", "inquiry", "palpation"] as const

export function analyze(symptomIds: string[], domain: Domain): Analysis {
  const present = new Set(symptomIds.filter((id) => symptomById.has(id)))
  const catalog = catalogFor(domain)
  const missingTongue = !symptoms.some((item) => present.has(item.id) && TONGUE_FIELDS.has(item.field))
  const missingPulse = !symptoms.some((item) => present.has(item.id) && PULSE_FIELDS.has(item.field))
  const tonguePulsePenalty = missingTongue && missingPulse ? 0.9 : 1

  const hits = crossFeatures.filter((feature) => feature.symptoms.every((id) => present.has(id)))
  const boost = crossBoost(present)

  const raw = catalog.map((syndrome) => {
    const base = profileScore(syndrome, present)
    const boosted = clamp(base.score + (boost.get(syndrome.id) ?? 0))
    return { syndrome, ...base, score: boosted * tonguePulsePenalty }
  })

  const adjusted = applyConstraints(raw)
  const ranked: RankedSyndrome[] = adjusted
    .map((row) => ({
      id: row.syndrome.id,
      score: row.score,
      band: bandFor(row.score),
      matchedKey: row.matchedKey,
      matchedSupport: row.matchedSupport,
      missingKey: row.missingKey,
      againstHits: row.againstHits,
    }))
    .sort((a, b) => b.score - a.score)

  const fields = new Set(symptoms.filter((item) => present.has(item.id)).map((item) => item.field))

  return {
    domain,
    ranked,
    crossHits: hits.map((feature) => ({
      id: feature.id,
      name: feature.name,
      note: feature.note,
      symptoms: [...feature.symptoms],
    })),
    exams: EXAMS.map((exam) => ({
      exam,
      label: EXAM_LABEL[exam],
      count: symptoms.filter((item) => item.exam === exam && present.has(item.id)).length,
    })),
    fieldsFilled: fields.size,
    fieldTotal: new Set(symptoms.map((item) => item.field)).size,
    missingTongue,
    missingPulse,
    constraints: constraintNotes(adjusted),
    symptomCount: present.size,
  }
}

function profileScore(syndrome: Syndrome, present: Set<string>) {
  let keyHit = 0
  let keyMax = 0
  let supportHit = 0
  let supportMax = 0
  const matchedKey: string[] = []
  const matchedSupport: string[] = []
  const missingKey: string[] = []

  for (const item of syndrome.key) {
    keyMax += item.weight
    if (present.has(item.id)) {
      keyHit += item.weight
      matchedKey.push(item.id)
    } else {
      missingKey.push(item.id)
    }
  }
  for (const item of syndrome.support) {
    supportMax += item.weight
    if (present.has(item.id)) {
      supportHit += item.weight
      matchedSupport.push(item.id)
    }
  }

  const keyCoverage = keyMax === 0 ? 0 : keyHit / keyMax
  const supportCoverage = supportMax === 0 ? 0 : supportHit / supportMax
  let score = 0.78 * keyCoverage + 0.22 * supportCoverage
  if (keyHit === 0) score *= 0.25
  const againstHits = syndrome.against.filter((id) => present.has(id))
  score -= againstHits.length * 0.07
  missingKey.sort((a, b) => {
    const wa = syndrome.key.find((item) => item.id === a)?.weight ?? 0
    const wb = syndrome.key.find((item) => item.id === b)?.weight ?? 0
    return wb - wa
  })

  return {
    score: clamp(score),
    matchedKey,
    matchedSupport,
    missingKey: missingKey.slice(0, 4),
    againstHits,
  }
}

function applyConstraints<T extends { syndrome: Syndrome; score: number }>(rows: T[]): T[] {
  const groups = new Map<string, T[]>()
  for (const row of rows) {
    if (!row.syndrome.constraint) continue
    const list = groups.get(row.syndrome.constraint) ?? []
    list.push(row)
    groups.set(row.syndrome.constraint, list)
  }
  const next = new Map<string, number>()
  for (const list of groups.values()) {
    if (list.length < 2) continue
    const temperature = 0.18
    const exps = list.map((row) => Math.exp(row.score / temperature))
    const sum = exps.reduce((total, value) => total + value, 0)
    list.forEach((row, index) => {
      const share = exps[index] / sum
      next.set(row.syndrome.id, clamp(row.score * (0.7 + 0.3 * share)))
    })
  }
  return rows.map((row) => (next.has(row.syndrome.id) ? { ...row, score: next.get(row.syndrome.id)! } : row))
}

function constraintNotes(rows: { syndrome: Syndrome; score: number }[]): ConstraintNote[] {
  const groups = new Map<string, { syndrome: Syndrome; score: number }[]>()
  for (const row of rows) {
    if (!row.syndrome.constraint) continue
    const list = groups.get(row.syndrome.constraint) ?? []
    list.push(row)
    groups.set(row.syndrome.constraint, list)
  }
  const notes: ConstraintNote[] = []
  for (const [group, list] of groups) {
    const sorted = [...list].sort((a, b) => b.score - a.score)
    if (sorted.length < 2 || sorted[0].score < 0.2) continue
    const leader = sorted[0]
    const trailer = sorted[1]
    notes.push({
      group: group as ConstraintNote["group"],
      leaderId: leader.syndrome.id,
      trailerId: trailer.syndrome.id,
      note: `${leader.syndrome.name} is ahead of ${trailer.syndrome.name.toLowerCase()} in this competing pair.`,
    })
  }
  return notes
}

export function bandFor(score: number): Band {
  if (score >= SUGGEST_AT) return "suggested"
  if (score >= CONSIDER_AT) return "consider"
  return "low"
}

export function clamp(value: number): number {
  return Math.max(0, Math.min(1, value))
}

let teachingCache: TeachingCase[] | null = null

export function teachingCases(): TeachingCase[] {
  if (!teachingCache) teachingCache = buildTeachingCases()
  return teachingCache
}

function buildTeachingCases(): TeachingCase[] {
  const cases: TeachingCase[] = showcaseCases.map((item) => ({
    id: item.id,
    domain: item.domain,
    symptoms: item.symptoms,
    labels: goldLabels(item.domain, item.symptoms, [item.primary]),
    source: "showcase",
    title: item.title,
  }))

  const rand = mulberry32(340)
  syndromes.forEach((syndrome, syndromeIndex) => {
    const copies = syndrome.layer === "disease" ? 4 : 2
    for (let copy = 0; copy < copies; copy += 1) {
      const domain = syndrome.layer === "disease" ? syndrome.domains[0] : "holistic"
      const symptomsKept = new Set<string>()
      for (const item of syndrome.key) {
        if (rand() > 0.18) symptomsKept.add(item.id)
      }
      for (const item of syndrome.support) {
        if (rand() < 0.55) symptomsKept.add(item.id)
      }
      if (symptomsKept.size < 4) {
        for (const item of syndrome.key) symptomsKept.add(item.id)
      }
      if (rand() < 0.22 && syndrome.companions.length > 0) {
        const companion = syndromeById.get(syndrome.companions[Math.floor(rand() * syndrome.companions.length)])
        if (companion && (companion.layer !== "disease" || companion.domains.includes(domain))) {
          for (const item of companion.key) {
            if (rand() < 0.55) symptomsKept.add(item.id)
          }
        }
      }
      if (rand() < 0.4) {
        const other = syndromes[Math.floor(rand() * syndromes.length)]
        const distractor = other.key[Math.floor(rand() * other.key.length)]
        if (distractor && !syndrome.against.includes(distractor.id) && other.id !== syndrome.id) {
          symptomsKept.add(distractor.id)
        }
      }
      const symptomList = Array.from(symptomsKept)
      cases.push({
        id: `syn-${syndromeIndex}-${copy}`,
        domain,
        symptoms: symptomList,
        labels: goldLabels(domain, symptomList, [syndrome.id]),
        source: "synthetic",
      })
    }
  })

  return cases
}

function goldLabels(domain: Domain, symptomIds: string[], seeds: string[]): string[] {
  const present = new Set(symptomIds)
  const catalog = catalogFor(domain)
  const labels = new Set<string>()
  for (const seed of seeds) {
    labels.add(seed)
    const syndrome = syndromeById.get(seed)
    if (!syndrome) continue
    for (const implied of syndrome.implies) {
      if (catalog.some((item) => item.id === implied)) labels.add(implied)
    }
  }
  for (const syndrome of catalog) {
    if (syndrome.layer === "disease" && !seeds.includes(syndrome.id)) continue
    const coverage = keyCoverage(syndrome, present)
    if (coverage >= 0.62) labels.add(syndrome.id)
  }
  return Array.from(labels)
}

function keyCoverage(syndrome: Syndrome, present: Set<string>): number {
  const max = syndrome.key.reduce((total, item) => total + item.weight, 0)
  if (max === 0) return 0
  const hit = syndrome.key.reduce((total, item) => total + (present.has(item.id) ? item.weight : 0), 0)
  return hit / max
}

function mulberry32(seed: number) {
  let state = seed
  return () => {
    state |= 0
    state = (state + 0x6d2b79f5) | 0
    let t = Math.imul(state ^ (state >>> 15), 1 | state)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export type MetricRow = {
  model: string
  exampleF1: number
  hamming: number
  averagePrecision: number
  oneError: number
  subsetAccuracy: number
}

export function labReport(): { rows: MetricRow[]; cases: number; relief: { id: string; weight: number }[] } {
  const cases = teachingCases()
  const ranker = cases.map((item) => {
    const analysis = analyze(item.symptoms, item.domain)
    const scores = new Map(analysis.ranked.map((row) => [row.id, row.score]))
    return scoreCase(item, scores, CONSIDER_AT)
  })
  const baseline = cases.map((item) => scoreCase(item, baselineScores(item), 0.34))
  const neighbors = mlknnLeaveOneOut(cases)

  return {
    cases: cases.length,
    rows: [
      summarize("Pattern ranker", ranker),
      summarize("Overlap baseline", baseline),
      summarize("ML-KNN, leave one out", neighbors),
    ],
    relief: reliefRanking().slice(0, 12),
  }
}

type ScoredCase = {
  gold: Set<string>
  ranked: string[]
  predicted: Set<string>
  labelSpace: string[]
}

function scoreCase(item: TeachingCase, scores: Map<string, number>, threshold: number): ScoredCase {
  const labelSpace = catalogFor(item.domain).map((syndrome) => syndrome.id)
  const ranked = [...labelSpace].sort((a, b) => (scores.get(b) ?? 0) - (scores.get(a) ?? 0))
  const predicted = new Set(labelSpace.filter((id) => (scores.get(id) ?? 0) >= threshold))
  return { gold: new Set(item.labels.filter((id) => labelSpace.includes(id))), ranked, predicted, labelSpace }
}

function baselineScores(item: TeachingCase): Map<string, number> {
  const present = new Set(item.symptoms)
  const scores = new Map<string, number>()
  for (const syndrome of catalogFor(item.domain)) {
    const pool = [...syndrome.key, ...syndrome.support].map((entry) => entry.id)
    const unique = Array.from(new Set(pool))
    if (unique.length === 0) {
      scores.set(syndrome.id, 0)
      continue
    }
    const hit = unique.filter((id) => present.has(id)).length
    scores.set(syndrome.id, hit / unique.length)
  }
  return scores
}

function summarize(model: string, scored: ScoredCase[]): MetricRow {
  const exampleF1 = mean(scored.map((item) => f1(item.gold, item.predicted)))
  let hammingMistakes = 0
  let hammingCells = 0
  let oneErrors = 0
  let exact = 0
  const aps: number[] = []
  for (const item of scored) {
    hammingCells += item.labelSpace.length
    for (const id of item.labelSpace) {
      const wanted = item.gold.has(id)
      const got = item.predicted.has(id)
      if (wanted !== got) hammingMistakes += 1
    }
    if (item.ranked.length === 0 || !item.gold.has(item.ranked[0])) oneErrors += 1
    if (sameSet(item.gold, item.predicted)) exact += 1
    aps.push(averagePrecision(item.ranked, item.gold))
  }
  return {
    model,
    exampleF1,
    hamming: hammingCells === 0 ? 0 : hammingMistakes / hammingCells,
    averagePrecision: mean(aps),
    oneError: scored.length === 0 ? 0 : oneErrors / scored.length,
    subsetAccuracy: scored.length === 0 ? 0 : exact / scored.length,
  }
}

function mlknnLeaveOneOut(cases: TeachingCase[]): ScoredCase[] {
  const k = 5
  const vectors = cases.map((item) => symptomVector(item.symptoms))
  return cases.map((item, index) => {
    const distances = vectors.map((vector, other) => ({
      other,
      distance: other === index ? Number.POSITIVE_INFINITY : hammingDistance(vectors[index], vector),
    }))
    distances.sort((a, b) => a.distance - b.distance)
    const neighborhood = distances.slice(0, k).map((entry) => cases[entry.other])
    const labelSpace = catalogFor(item.domain).map((syndrome) => syndrome.id)
    const scores = new Map<string, number>()
    for (const id of labelSpace) {
      const votes = neighborhood.filter((neighbor) => neighbor.labels.includes(id) && catalogFor(neighbor.domain).some((syndrome) => syndrome.id === id)).length
      const prior = cases.filter((row, rowIndex) => rowIndex !== index && row.labels.includes(id)).length / Math.max(1, cases.length - 1)
      const posterior = (votes + prior) / (k + 1)
      scores.set(id, posterior)
    }
    return scoreCase(item, scores, 0.45)
  })
}

function symptomVector(ids: string[]): Uint8Array {
  const vector = new Uint8Array(symptoms.length)
  const index = new Map(symptoms.map((item, position) => [item.id, position]))
  for (const id of ids) {
    const at = index.get(id)
    if (at !== undefined) vector[at] = 1
  }
  return vector
}

function hammingDistance(left: Uint8Array, right: Uint8Array): number {
  let distance = 0
  for (let index = 0; index < left.length; index += 1) {
    if (left[index] !== right[index]) distance += 1
  }
  return distance
}

let reliefCache: { id: string; weight: number }[] | null = null

export function reliefRanking(): { id: string; weight: number }[] {
  if (reliefCache) return reliefCache
  const cases = teachingCases()
  const vectors = cases.map((item) => symptomVector(item.symptoms))
  const weights = new Array(symptoms.length).fill(0)
  const k = 4
  cases.forEach((item, index) => {
    const others = cases.map((other, otherIndex) => ({
      otherIndex,
      jaccard: otherIndex === index ? -1 : jaccard(item.labels, other.labels),
    }))
    const hits = others.filter((entry) => entry.jaccard > 0).sort((a, b) => b.jaccard - a.jaccard).slice(0, k)
    const misses = others.filter((entry) => entry.jaccard === 0).sort((a, b) => hammingDistance(vectors[index], vectors[a.otherIndex]) - hammingDistance(vectors[index], vectors[b.otherIndex])).slice(0, k)
    for (let feature = 0; feature < symptoms.length; feature += 1) {
      const hitDiff = hits.length === 0 ? 0 : hits.reduce((total, entry) => total + Math.abs(vectors[index][feature] - vectors[entry.otherIndex][feature]), 0) / hits.length
      const missDiff = misses.length === 0 ? 0 : misses.reduce((total, entry) => total + Math.abs(vectors[index][feature] - vectors[entry.otherIndex][feature]), 0) / misses.length
      weights[feature] += missDiff - hitDiff
    }
  })
  const min = Math.min(...weights)
  const max = Math.max(...weights)
  reliefCache = symptoms
    .map((symptom, index) => ({
      id: symptom.id,
      weight: max === min ? 0 : (weights[index] - min) / (max - min),
    }))
    .sort((a, b) => b.weight - a.weight)
  return reliefCache
}

function jaccard(left: string[], right: string[]): number {
  const a = new Set(left)
  const b = new Set(right)
  let intersection = 0
  for (const id of a) if (b.has(id)) intersection += 1
  const union = a.size + b.size - intersection
  return union === 0 ? 0 : intersection / union
}

function f1(gold: Set<string>, predicted: Set<string>): number {
  let intersection = 0
  for (const id of predicted) if (gold.has(id)) intersection += 1
  if (gold.size === 0 && predicted.size === 0) return 1
  if (intersection === 0) return 0
  const precision = intersection / predicted.size
  const recall = intersection / gold.size
  return (2 * precision * recall) / (precision + recall)
}

function averagePrecision(ranked: string[], gold: Set<string>): number {
  if (gold.size === 0) return 0
  let hits = 0
  let sum = 0
  ranked.forEach((id, index) => {
    if (!gold.has(id)) return
    hits += 1
    sum += hits / (index + 1)
  })
  return sum / gold.size
}

function sameSet(left: Set<string>, right: Set<string>): boolean {
  if (left.size !== right.size) return false
  for (const id of left) if (!right.has(id)) return false
  return true
}

function mean(values: number[]): number {
  if (values.length === 0) return 0
  return values.reduce((total, value) => total + value, 0) / values.length
}

export function relatedDiseases(symptomIds: string[]): RankedSyndrome[] {
  const present = new Set(symptomIds.filter((id) => symptomById.has(id)))
  const boost = crossBoost(present)
  return syndromes
    .filter((syndrome) => syndrome.layer === "disease")
    .map((syndrome) => {
      const base = profileScore(syndrome, present)
      const score = clamp(base.score + (boost.get(syndrome.id) ?? 0))
      return {
        id: syndrome.id,
        score,
        band: bandFor(score),
        matchedKey: base.matchedKey,
        matchedSupport: base.matchedSupport,
        missingKey: base.missingKey,
        againstHits: base.againstHits,
      }
    })
    .filter((row) => row.band === "suggested")
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
}

export function neighborReading(symptomIds: string[], domain: Domain): { id: string; score: number }[] {
  const gallery = teachingCases().filter((item) => item.domain === domain)
  if (gallery.length === 0 || symptomIds.length === 0) return []
  const query = symptomVector(symptomIds)
  const nearest = gallery
    .map((item) => ({ item, distance: hammingDistance(query, symptomVector(item.symptoms)) }))
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 5)
  return catalogFor(domain)
    .map((syndrome) => {
      const votes = nearest.filter((entry) => entry.item.labels.includes(syndrome.id)).length
      return { id: syndrome.id, score: votes / nearest.length }
    })
    .filter((row) => row.score >= 0.4)
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
}

function crossBoost(present: Set<string>): Map<string, number> {
  const boost = new Map<string, number>()
  for (const feature of crossFeatures) {
    if (!feature.symptoms.every((id) => present.has(id))) continue
    for (const id of feature.boosts) boost.set(id, (boost.get(id) ?? 0) + 0.045)
  }
  return boost
}

export function cooccurrence(syndromeId: string): { symptoms: string[]; matrix: number[][]; cases: number } | null {
  const syndrome = syndromeById.get(syndromeId)
  if (!syndrome) return null
  const pool = Array.from(new Set([...syndrome.key, ...syndrome.support].map((item) => item.id))).slice(0, 8)
  const cases = teachingCases().filter((item) => item.labels.includes(syndromeId))
  if (cases.length === 0 || pool.length === 0) return { symptoms: pool, matrix: [], cases: 0 }
  const matrix = pool.map((row) => pool.map((column) => {
    const both = cases.filter((item) => item.symptoms.includes(row) && item.symptoms.includes(column)).length
    return both / cases.length
  }))
  return { symptoms: pool, matrix, cases: cases.length }
}
