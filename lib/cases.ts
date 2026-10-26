import type { ShowcaseCase } from "./types"

export const showcaseCases: ShowcaseCase[] = [
  {
    id: "kd-yang-damp",
    title: "Swollen ankles and a cold, heavy middle",
    domain: "kidney",
    primary: "spleen-kidney-yang-deficiency",
    narrative:
      "For three winters the lower back has been sore, the knees unreliable, and the ankles swollen by evening. The limbs are cold, the stool is loose, and the urine is long and clear. Appetite is poor with morning nausea. The face is bright white. The tongue is pale, swollen, and teeth-marked with a greasy coat. The pulse is deep, slow, and weak.",
    symptoms: [
      "fatigue", "cold-limbs", "lumbar-soreness", "knee-weakness", "lower-edema", "loose-stool",
      "clear-urine", "nausea", "poor-appetite", "bright-white-complexion", "pale-tongue", "swollen-tongue",
      "teeth-marks", "greasy-coat", "deep-pulse", "weak-pulse", "slow-pulse",
    ],
    note: "Yang deficiency and damp turbidity are meant to be called together, not collapsed into one label.",
  },
  {
    id: "kd-liver-yin",
    title: "Sore back, dry eyes, and night sweats",
    domain: "kidney",
    primary: "liver-kidney-yin-deficiency",
    narrative:
      "The lower back and knees ache. There is ringing in the ears, dizziness, and dry eyes by the end of the day. Sweats at night, heat in the palms, and a malar flush. The tongue is red with a scanty coat. The pulse is thin and rapid. Mood is irritable, but the appetite is ordinary.",
    symptoms: [
      "lumbar-soreness", "knee-weakness", "tinnitus", "dizziness", "dry-eyes", "night-sweat",
      "five-center-heat", "irritability", "red-tongue", "scanty-coat", "thin-pulse", "rapid-pulse", "malar-flush",
    ],
    note: "Empty heat without a greasy coat. Damp turbidity should stay quiet.",
  },
  {
    id: "kd-spleen-yin",
    title: "Dry mouth, scant appetite, sore back",
    domain: "kidney",
    primary: "spleen-kidney-yin-deficiency",
    narrative:
      "Low back soreness with a dry mouth, little appetite, and dry stool. Afternoon tidal fever and night sweats. The tongue is red with peeled patches. The pulse is thin and slightly rapid. Energy is low. There is tinnitus but the limbs are not cold.",
    symptoms: [
      "lumbar-soreness", "dry-mouth", "poor-appetite", "dry-stool", "tidal-fever", "night-sweat",
      "red-tongue", "peeled-coat", "thin-pulse", "rapid-pulse", "fatigue", "tinnitus",
    ],
    note: "Spleen participation is the appetite and the dry stool, which separates this from liver-kidney yin deficiency.",
  },
  {
    id: "st-liver",
    title: "Sighing, flank fullness, and acid",
    domain: "stomach",
    primary: "liver-stomach-disharmony",
    narrative:
      "Epigastric distension and acid reflux worsen when work is tense. Frequent sighing, irritability, and a low mood. The flanks feel full. Appetite is uneven. The tongue coat is thin and white. The pulse is wiry. There is nausea but no cold pain.",
    symptoms: [
      "epigastric-distension", "hypochondriac-distension", "acid-reflux", "sighing", "irritability",
      "depression", "wiry-pulse", "poor-appetite", "thin-white-coat", "nausea", "epigastric-pain",
    ],
    note: "A qi-stagnation stomach chart. Deficiency cold should not lead.",
  },
  {
    id: "st-cold",
    title: "Cold stomach pain that wants a warm hand",
    domain: "stomach",
    primary: "spleen-stomach-deficiency-cold",
    narrative:
      "Cold pain in the stomach, better with warmth and pressure. Poor appetite, loose stool, fatigue, and cold hands and feet. The face is pale. The tongue is pale and slightly swollen with a thin white coat. The pulse is deep, slow, and weak.",
    symptoms: [
      "epigastric-cold-pain", "prefers-warmth-pressure", "poor-appetite", "loose-stool", "fatigue",
      "cold-limbs", "pale-complexion", "pale-tongue", "swollen-tongue", "thin-white-coat",
      "deep-pulse", "slow-pulse", "weak-pulse",
    ],
    note: "Empty cold in the middle burner. Pressure helps, so food stagnation should lose.",
  },
  {
    id: "st-damp-heat",
    title: "Bitter taste and a yellow greasy coat",
    domain: "stomach",
    primary: "spleen-stomach-damp-heat",
    narrative:
      "The stomach feels full. Nausea, sticky stool, foul breath, and a bitter taste. Urine is dark and scanty. The body feels heavy. The tongue is red with a yellow greasy coat. The pulse is slippery and rapid.",
    symptoms: [
      "epigastric-distension", "nausea", "sticky-stool", "foul-breath", "bitter-taste",
      "yellow-greasy-coat", "red-tongue", "slippery-pulse", "rapid-pulse", "dark-urine",
      "heavy-body", "poor-appetite",
    ],
    note: "Damp-heat can share the chart with food stagnation because foul breath and fullness are present. Damp-heat should still lead.",
  },
  {
    id: "st-yin",
    title: "Hunger without wanting to eat",
    domain: "stomach",
    primary: "stomach-yin-deficiency",
    narrative:
      "Dry mouth, epigastric pain, and little desire to eat. Stool is dry and constipation is frequent. Heat in the palms. The tongue is red, thin, and peeled. The pulse is thin and rapid. No greasy coat and no cold limbs.",
    symptoms: [
      "dry-mouth", "epigastric-pain", "poor-appetite", "constipation", "dry-stool", "red-tongue",
      "peeled-coat", "thin-tongue", "thin-pulse", "rapid-pulse", "five-center-heat",
    ],
    note: "Stomach yin deficiency. The peeled coat is the cross-feature that should suppress damp-heat.",
  },
  {
    id: "st-food",
    title: "Foul breath after a heavy meal",
    domain: "stomach",
    primary: "food-stagnation",
    narrative:
      "Since a large meal, the epigastrium is distended and refuses pressure. Foul breath, acid reflux, nausea, and constipation. The coat is thick, white, and greasy. The pulse is slippery. Pain is worse, not better, when pressed.",
    symptoms: [
      "epigastric-distension", "foul-breath", "acid-reflux", "refuses-pressure", "greasy-coat",
      "thick-white-coat", "slippery-pulse", "constipation", "nausea", "abdominal-distension", "vomiting",
    ],
    note: "Fullness that refuses pressure. Deficiency cold likes pressure and should stay low.",
  },
  {
    id: "dy-qi-stasis",
    title: "Distending period pain and dark clots",
    domain: "dysmenorrhea",
    primary: "qi-stagnation-blood-stasis",
    narrative:
      "Before the period the lower abdomen distends and aches. The menses are dark with clots, and the pain eases after the clots pass. The period is late. Flank distension, irritability, and sighing. The tongue is purple with petechiae. The pulse is wiry and choppy.",
    symptoms: [
      "lower-abd-distend-pain", "dark-clots", "pain-eases-after-clots", "hypochondriac-distension",
      "irritability", "sighing", "wiry-pulse", "purple-tongue", "petechiae", "choppy-pulse", "delayed-period",
    ],
    note: "The single disease class used for this presentation still should light qi stagnation and blood stasis as separate holistic tags.",
  },
  {
    id: "dy-cold-stasis",
    title: "Cold lower abdomen, eased by heat",
    domain: "dysmenorrhea",
    primary: "congealing-cold-stasis",
    narrative:
      "Cold pain in the lower abdomen during the period, relieved by a hot water bottle. The period is late and dark with clots. Cold hands and feet. The abdomen feels cold. The face is pale. The tongue is pale with purple areas and a thick white coat. The pulse is tight and choppy.",
    symptoms: [
      "lower-abd-cold-pain", "cold-pain-better-warmth", "dark-clots", "delayed-period", "cold-limbs",
      "pale-complexion", "thick-white-coat", "pale-tongue", "purple-tongue", "tight-pulse", "choppy-pulse", "abdomen-cold",
    ],
    note: "Cold and stasis together. Yang-deficiency internal cold prefers pale menses without clots.",
  },
  {
    id: "dy-empty",
    title: "Dull period pain in a pale, tired patient",
    domain: "dysmenorrhea",
    primary: "qi-blood-deficiency",
    narrative:
      "The period pain is a dull ache and feels better with warmth and pressure. Fatigue, a low voice, dizziness, pale face, pale lips, and pale nails. Menses are scanty and pale. The tongue is pale. The pulse is thin and weak.",
    symptoms: [
      "dull-period-pain", "prefers-warmth-pressure", "fatigue", "lassitude", "pale-complexion",
      "pale-lips", "pale-nails", "dizziness", "low-voice", "scanty-pale-menses", "pale-tongue",
      "thin-pulse", "weak-pulse",
    ],
    note: "Empty pain and pale blood. Stasis markers are absent on purpose.",
  },
  {
    id: "dy-damp-heat",
    title: "Burning period pain, yellow greasy coat",
    domain: "dysmenorrhea",
    primary: "damp-heat-stasis",
    narrative:
      "Burning pain in the lower abdomen, an early period, and dark clots. Stool is sticky and urine is dark. Bitter taste and irritability, with some flank distension. The tongue is red with a yellow greasy coat. The pulse is slippery and rapid.",
    symptoms: [
      "lower-abd-burning", "early-period", "dark-clots", "sticky-stool", "dark-urine", "bitter-taste",
      "yellow-greasy-coat", "red-tongue", "slippery-pulse", "rapid-pulse", "irritability", "hypochondriac-distension",
    ],
    note: "Damp-heat stasis should lead. Liver constraint with damp-heat is a fair second, because the flank and the mood are also in the chart.",
  },
  {
    id: "dy-yang",
    title: "Bright-white face and a cold, pale period",
    domain: "dysmenorrhea",
    primary: "yang-deficiency-internal-cold",
    narrative:
      "Bright white complexion, cold limbs, and cold period pain relieved by warmth. Urine is clear and abundant. Menses are scanty and pale, and the period is late. The tongue is pale and swollen. The pulse is deep, slow, and weak. No clots.",
    symptoms: [
      "bright-white-complexion", "cold-limbs", "cold-pain-better-warmth", "clear-urine",
      "scanty-pale-menses", "dull-period-pain", "lower-abd-cold-pain", "swollen-tongue", "pale-tongue",
      "deep-pulse", "slow-pulse", "weak-pulse", "fatigue", "delayed-period",
    ],
    note: "Internal cold from yang deficiency, kept apart from congealing cold because the menses are pale.",
  },
  {
    id: "ho-exterior",
    title: "Chills, body ache, floating pulse",
    domain: "holistic",
    primary: "exterior",
    narrative:
      "Two days of chills and fever, headache, and a generalized ache. No thirst. The tongue coat is thin and white. The pulse is floating and tight. No low-back disease and no deep pulse.",
    symptoms: ["aversion-cold", "fever", "body-aches", "headache", "floating-pulse", "thin-white-coat", "tight-pulse", "thirst-none"],
    note: "A surface pattern. Interior should lose the exterior-interior contest.",
  },
  {
    id: "ho-phlegm",
    title: "Chest oppression and watery phlegm",
    domain: "holistic",
    primary: "phlegm-fluid",
    narrative:
      "Chest tightness, cough with copious clear phlegm, and a heavy body. Nausea and dizziness. Build is heavy. The tongue is swollen with a greasy coat. The pulse is slippery and soggy.",
    symptoms: [
      "chest-oppression", "cough", "clear-phlegm", "greasy-coat", "swollen-tongue", "slippery-pulse",
      "nausea", "dizziness", "overweight", "heavy-body", "soggy-pulse",
    ],
    note: "Phlegm-fluid as a holistic pathology label, with the lung organ tag expected beside it.",
  },
  {
    id: "ho-blood",
    title: "Palpitations, pale nails, poor sleep",
    domain: "holistic",
    primary: "blood-deficiency",
    narrative:
      "Palpitations, insomnia, and dream-disturbed sleep. Dizzy at times. The face, lips, and nails are pale. The tongue is pale. The pulse is thin and weak.",
    symptoms: [
      "palpitations", "insomnia", "dream-sleep", "pale-complexion", "pale-lips", "pale-nails",
      "dizziness", "pale-tongue", "thin-pulse", "weak-pulse",
    ],
    note: "Blood deficiency located at the heart. The organ tag and the pathology tag are both part of the answer.",
  },
  {
    id: "ho-qi",
    title: "Sighing, flank distension, wiry pulse",
    domain: "holistic",
    primary: "qi-stagnation",
    narrative:
      "Frequent sighing, flank distension and ache, irritability, and a low mood. The abdomen distends when tense. Tongue coat is thin and white. The pulse is wiry. No clots and no purple tongue.",
    symptoms: [
      "hypochondriac-distension", "hypochondriac-pain", "sighing", "irritability", "depression",
      "wiry-pulse", "abdominal-distension", "thin-white-coat",
    ],
    note: "Qi stagnation without stasis. Blood stasis should stay below the line.",
  },
]
