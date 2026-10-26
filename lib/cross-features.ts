export type CrossFeature = {
  id: string
  name: string
  symptoms: [string, string]
  boosts: string[]
  note: string
}

export const crossFeatures: CrossFeature[] = [
  {
    id: "pale-weak",
    name: "Pale tongue × weak pulse",
    symptoms: ["pale-tongue", "weak-pulse"],
    boosts: ["qi-deficiency", "blood-deficiency", "qi-blood-deficiency", "deficiency", "spleen-stomach-deficiency-cold"],
    note: "A tongue-pulse cross that usually travels with qi or blood deficiency.",
  },
  {
    id: "purple-choppy",
    name: "Purple tongue × choppy pulse",
    symptoms: ["purple-tongue", "choppy-pulse"],
    boosts: ["blood-stasis", "qi-stagnation-blood-stasis", "congealing-cold-stasis", "kidney-deficiency-blood-stasis"],
    note: "Local evidence for stasis that a bag-of-symptoms can underweight.",
  },
  {
    id: "yellow-slippery",
    name: "Yellow greasy coat × slippery pulse",
    symptoms: ["yellow-greasy-coat", "slippery-pulse"],
    boosts: ["spleen-stomach-damp-heat", "damp-heat-stasis", "liver-constraint-damp-heat", "heat", "excess"],
    note: "Coat and pulse crossing toward damp-heat rather than empty heat.",
  },
  {
    id: "cold-deep",
    name: "Cold limbs × deep pulse",
    symptoms: ["cold-limbs", "deep-pulse"],
    boosts: ["deficiency-cold", "cold", "spleen-kidney-yang-deficiency", "yang-deficiency-internal-cold", "interior"],
    note: "Cold that has reached the interior, rather than a floating exterior chill.",
  },
  {
    id: "red-rapid",
    name: "Red tongue × rapid pulse",
    symptoms: ["red-tongue", "rapid-pulse"],
    boosts: ["heat", "excess-heat", "deficiency-heat"],
    note: "The smallest heat cross. Scanty coat then tips it toward empty heat.",
  },
  {
    id: "wiry-flank",
    name: "Wiry pulse × flank distension",
    symptoms: ["wiry-pulse", "hypochondriac-distension"],
    boosts: ["qi-stagnation", "liver", "liver-stomach-disharmony", "liver-constraint-damp-heat", "qi-stagnation-blood-stasis"],
    note: "A liver-qi cross used in both stomach and menstrual charts.",
  },
  {
    id: "night-scanty",
    name: "Night sweats × scanty coat",
    symptoms: ["night-sweat", "scanty-coat"],
    boosts: ["deficiency-heat", "liver-kidney-yin-deficiency"],
    note: "Empty heat rather than a greasy, phlegm, or damp chart.",
  },
  {
    id: "clots-cold-pain",
    name: "Dark clots × cold lower-abdominal pain",
    symptoms: ["dark-clots", "lower-abd-cold-pain"],
    boosts: ["congealing-cold-stasis", "blood-stasis", "cold"],
    note: "Cold and stasis confirmed together, which is the dysmenorrhea class, not pale yang deficiency.",
  },
  {
    id: "floating-chill",
    name: "Floating pulse × aversion to cold",
    symptoms: ["floating-pulse", "aversion-cold"],
    boosts: ["exterior", "excess-cold", "cold"],
    note: "The surface cross. A deep pulse should not be in the same chart.",
  },
  {
    id: "greasy-nausea",
    name: "Greasy coat × nausea",
    symptoms: ["greasy-coat", "nausea"],
    boosts: ["damp-turbidity", "phlegm-fluid", "spleen-stomach-damp-heat", "food-stagnation"],
    note: "Turbid dampness in the middle, shared by kidney and stomach lenses.",
  },
]
