export type Exam = "inspection" | "listening" | "inquiry" | "palpation"

export type Domain = "holistic" | "kidney" | "stomach" | "dysmenorrhea"

export type Layer = "principle" | "organ" | "pathology" | "disease"

export type ConstraintGroup = "exterior-interior" | "cold-heat" | "deficiency-excess"

export type Symptom = {
  id: string
  name: string
  chinese: string
  exam: Exam
  field: string
  aliases: string[]
}

export type SymptomWeight = {
  id: string
  weight: number
}

export type Syndrome = {
  id: string
  name: string
  chinese: string
  pinyin: string
  layer: Layer
  domains: Domain[]
  summary: string
  reading: string
  key: SymptomWeight[]
  support: SymptomWeight[]
  against: string[]
  companions: string[]
  implies: string[]
  constraint?: ConstraintGroup
  pole?: string
}

export type ShowcaseCase = {
  id: string
  title: string
  domain: Domain
  narrative: string
  symptoms: string[]
  primary: string
  note: string
}

export type TeachingCase = {
  id: string
  domain: Domain
  symptoms: string[]
  labels: string[]
  source: "showcase" | "synthetic"
  title?: string
}

export type Band = "suggested" | "consider" | "low"

export type RankedSyndrome = {
  id: string
  score: number
  band: Band
  matchedKey: string[]
  matchedSupport: string[]
  missingKey: string[]
  againstHits: string[]
}

export type CrossHit = {
  id: string
  name: string
  note: string
  symptoms: string[]
}

export type ConstraintNote = {
  group: ConstraintGroup
  leaderId: string
  trailerId: string
  note: string
}

export type Analysis = {
  domain: Domain
  ranked: RankedSyndrome[]
  crossHits: CrossHit[]
  exams: { exam: Exam; label: string; count: number }[]
  fieldsFilled: number
  fieldTotal: number
  missingTongue: boolean
  missingPulse: boolean
  constraints: ConstraintNote[]
  symptomCount: number
}
