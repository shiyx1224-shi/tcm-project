import type { Exam, Symptom } from "./types"

function symptom(
  id: string,
  name: string,
  chinese: string,
  exam: Exam,
  field: string,
  aliases: string[],
): Symptom {
  return {
    id,
    name,
    chinese,
    exam,
    field,
    aliases: Array.from(new Set([name.toLowerCase(), chinese, ...aliases.map((alias) => alias.toLowerCase())])),
  }
}

export const EXAM_LABEL: Record<Exam, string> = {
  inspection: "Inspection",
  listening: "Listening and smelling",
  inquiry: "Inquiry",
  palpation: "Palpation",
}

export const EXAM_CHINESE: Record<Exam, string> = {
  inspection: "望",
  listening: "闻",
  inquiry: "问",
  palpation: "切",
}

export const symptoms: Symptom[] = [
  symptom("pale-complexion", "Pale complexion", "面色淡白", "inspection", "Complexion", ["pale face", "pale looking", "wan complexion"]),
  symptom("red-complexion", "Red complexion", "面色红", "inspection", "Complexion", ["flushed face", "red face", "reddish complexion"]),
  symptom("sallow-complexion", "Sallow complexion", "面色萎黄", "inspection", "Complexion", ["sallow face", "yellowish complexion"]),
  symptom("bright-white-complexion", "Bright white complexion", "面色㿠白", "inspection", "Complexion", ["bright white face", "pallor"]),
  symptom("dark-complexion", "Dark complexion", "面色晦暗", "inspection", "Complexion", ["dusky complexion", "dark face", "dull complexion"]),
  symptom("malar-flush", "Malar flush", "颧红", "inspection", "Complexion", ["red cheeks", "flushed cheeks"]),
  symptom("pale-lips", "Pale lips", "唇淡", "inspection", "Complexion", ["pale lip"]),
  symptom("purple-lips", "Purple lips", "唇紫", "inspection", "Complexion", ["dusky lips", "cyanotic lips"]),
  symptom("pale-nails", "Pale nails", "爪甲淡白", "inspection", "Complexion", ["pale nail beds", "pale fingernails"]),
  symptom("thin-body", "Thin body", "形体消瘦", "inspection", "Physique", ["underweight", "emaciated", "thin build"]),
  symptom("overweight", "Heavy body build", "形体肥胖", "inspection", "Physique", ["overweight", "obesity"]),
  symptom("facial-edema", "Facial edema", "面目浮肿", "inspection", "Physique", ["puffy face", "swollen face"]),
  symptom("limb-edema", "Limb edema", "肢体浮肿", "inspection", "Physique", ["swollen limbs", "edema of the limbs"]),
  symptom("lower-edema", "Lower-limb edema", "下肢浮肿", "inspection", "Physique", ["swollen ankles", "ankle swelling", "leg edema", "pitting edema of the legs"]),
  symptom("pale-tongue", "Pale tongue", "舌淡", "inspection", "Tongue body", ["tongue is pale", "pale tongue body"]),
  symptom("red-tongue", "Red tongue", "舌红", "inspection", "Tongue body", ["tongue is red", "red tongue body"]),
  symptom("dark-tongue", "Dark tongue", "舌暗", "inspection", "Tongue body", ["dusky tongue", "dark tongue body"]),
  symptom("purple-tongue", "Purple tongue", "舌紫", "inspection", "Tongue body", ["purplish tongue", "tongue is purple"]),
  symptom("swollen-tongue", "Pale swollen tongue", "舌淡胖", "inspection", "Tongue body", ["swollen tongue", "enlarged tongue", "fat tongue", "pale enlarged tongue"]),
  symptom("thin-tongue", "Thin tongue", "舌瘦薄", "inspection", "Tongue body", ["thin tongue body", "small tongue"]),
  symptom("teeth-marks", "Teeth-marked tongue", "舌有齿痕", "inspection", "Tongue body", ["scalloped tongue", "tooth marks", "teeth marks on tongue"]),
  symptom("petechiae", "Tongue petechiae", "舌有瘀点", "inspection", "Tongue body", ["petechiae on tongue", "purple spots on tongue"]),
  symptom("thin-white-coat", "Thin white coat", "苔薄白", "inspection", "Tongue coat", ["thin white tongue coat", "white coat", "light white coating"]),
  symptom("thick-white-coat", "Thick white coat", "苔白厚", "inspection", "Tongue coat", ["thick white tongue coat", "thick white coating"]),
  symptom("yellow-coat", "Yellow coat", "苔黄", "inspection", "Tongue coat", ["yellow tongue coat", "yellow coating"]),
  symptom("greasy-coat", "Greasy coat", "苔腻", "inspection", "Tongue coat", ["greasy tongue coat", "slimy coat", "greasy coating"]),
  symptom("yellow-greasy-coat", "Yellow greasy coat", "苔黄腻", "inspection", "Tongue coat", ["yellow greasy tongue coat", "yellow slimy coat"]),
  symptom("scanty-coat", "Scanty coat", "苔少", "inspection", "Tongue coat", ["little coating", "scanty tongue coat", "thin coat almost none"]),
  symptom("peeled-coat", "Peeled coat", "苔剥", "inspection", "Tongue coat", ["peeled tongue coat", "geographic tongue", "bare tongue patches"]),
  symptom("low-voice", "Low voice", "声低", "listening", "Voice", ["weak voice", "quiet voice", "speaks softly"]),
  symptom("sighing", "Frequent sighing", "善太息", "listening", "Voice", ["sighing", "sighs often", "frequent sighs"]),
  symptom("foul-breath", "Foul breath", "口臭", "listening", "Breath", ["bad breath", "halitosis"]),
  symptom("borborygmus", "Borborygmus", "肠鸣", "listening", "Breath", ["stomach gurgling", "bowel sounds", "gurgling abdomen"]),
  symptom("fatigue", "Fatigue", "乏力", "inquiry", "Energy", ["tired", "fatigue", "no energy", "lack of strength", "exhausted"]),
  symptom("lassitude", "Lassitude of spirit", "神疲", "inquiry", "Energy", ["listless", "spiritless", "low spirits"]),
  symptom("spontaneous-sweat", "Spontaneous sweating", "自汗", "inquiry", "Sweat", ["sweats without exertion", "sweating easily", "spontaneous sweat"]),
  symptom("night-sweat", "Night sweating", "盗汗", "inquiry", "Sweat", ["night sweats", "sweats at night", "night sweat"]),
  symptom("aversion-cold", "Aversion to cold", "恶寒", "inquiry", "Cold and heat", ["chills", "aversion to wind", "feels cold", "fear of cold"]),
  symptom("aversion-heat", "Aversion to heat", "恶热", "inquiry", "Cold and heat", ["dislikes heat", "averse to heat"]),
  symptom("fever", "Fever", "发热", "inquiry", "Cold and heat", ["feverish", "has a fever"]),
  symptom("tidal-fever", "Tidal fever", "潮热", "inquiry", "Cold and heat", ["afternoon fever", "low grade fever in the afternoon", "tidal heat"]),
  symptom("cold-limbs", "Cold limbs", "四肢不温", "inquiry", "Cold and heat", ["cold hands and feet", "cold hands", "cold feet", "limbs feel cold"]),
  symptom("five-center-heat", "Five-center heat", "五心烦热", "inquiry", "Cold and heat", ["heat in palms and soles", "hot palms", "five center heat", "heat in the chest palms and soles"]),
  symptom("thirst-cold", "Thirst for cold drinks", "口渴喜冷饮", "inquiry", "Thirst", ["thirsty for cold drinks", "wants cold water", "prefers cold drinks"]),
  symptom("thirst-none", "No thirst", "口不渴", "inquiry", "Thirst", ["not thirsty", "no desire to drink"]),
  symptom("dry-mouth", "Dry mouth", "口干", "inquiry", "Thirst", ["dry mouth", "mouth feels dry"]),
  symptom("poor-appetite", "Poor appetite", "食欲不振", "inquiry", "Diet", ["no appetite", "low appetite", "poor intake", "does not want to eat", "torpid intake"]),
  symptom("nausea", "Nausea", "恶心", "inquiry", "Diet", ["nauseated", "feels sick to the stomach", "queasy"]),
  symptom("vomiting", "Vomiting", "呕吐", "inquiry", "Diet", ["vomits", "throwing up"]),
  symptom("acid-reflux", "Acid reflux", "反酸", "inquiry", "Diet", ["acid regurgitation", "heartburn", "sour regurgitation"]),
  symptom("epigastric-distension", "Epigastric distension", "胃脘胀", "inquiry", "Pain", ["stomach bloating", "bloating in the stomach", "epigastric fullness", "upper abdominal bloating"]),
  symptom("epigastric-pain", "Epigastric pain", "胃脘痛", "inquiry", "Pain", ["stomach pain", "epigastric ache", "pain in the stomach"]),
  symptom("epigastric-cold-pain", "Cold epigastric pain", "胃脘冷痛", "inquiry", "Pain", ["cold pain in the stomach", "stomach feels cold and painful"]),
  symptom("prefers-warmth-pressure", "Pain better with warmth and pressure", "喜温喜按", "inquiry", "Pain", ["better with pressure", "likes warmth and pressure", "pain relieved by warmth and pressure"]),
  symptom("refuses-pressure", "Pain worse with pressure", "拒按", "inquiry", "Pain", ["refuses pressure", "tender to touch", "worse with pressure"]),
  symptom("hypochondriac-distension", "Hypochondriac distension", "胁胀", "inquiry", "Pain", ["flank distension", "distension in the ribs", "hypochondriac fullness", "side of the chest feels full"]),
  symptom("hypochondriac-pain", "Hypochondriac pain", "胁痛", "inquiry", "Pain", ["flank pain", "rib-side pain", "hypochondriac ache"]),
  symptom("irritability", "Irritability", "烦躁易怒", "inquiry", "Emotion", ["irritable", "easily angered", "short tempered"]),
  symptom("depression", "Low mood", "情绪抑郁", "inquiry", "Emotion", ["depressed mood", "low mood", "feels down"]),
  symptom("abdominal-distension", "Abdominal distension", "腹胀", "inquiry", "Pain", ["abdominal bloating", "bloated abdomen", "belly distension"]),
  symptom("lower-abd-pain", "Lower abdominal pain", "少腹痛", "inquiry", "Pain", ["lower belly pain", "pain in the lower abdomen"]),
  symptom("lower-abd-cold-pain", "Cold lower abdominal pain", "少腹冷痛", "inquiry", "Pain", ["cold pain in the lower abdomen", "cold period pain", "lower abdomen feels cold and painful"]),
  symptom("lower-abd-distend-pain", "Distending lower abdominal pain", "少腹胀痛", "inquiry", "Pain", ["distending period pain", "period pain with bloating", "distending pain before the period"]),
  symptom("lower-abd-burning", "Burning lower abdominal pain", "少腹灼痛", "inquiry", "Pain", ["burning period pain", "burning pain in the lower abdomen"]),
  symptom("dull-period-pain", "Dull menstrual pain", "经行隐痛", "inquiry", "Menstruation", ["dull period pain", "dull ache during the period", "menstrual ache"]),
  symptom("heavy-body", "Heavy body", "身体困重", "inquiry", "Pain", ["body feels heavy", "heavy limbs", "heaviness"]),
  symptom("body-aches", "Body aches", "身痛", "inquiry", "Pain", ["aching body", "generalized aches", "body pain"]),
  symptom("headache", "Headache", "头痛", "inquiry", "Pain", ["head pain", "headaches"]),
  symptom("loose-stool", "Loose stool", "便溏", "inquiry", "Stool and urine", ["loose stools", "soft stool", "diarrhea", "loose bowels"]),
  symptom("constipation", "Constipation", "便秘", "inquiry", "Stool and urine", ["constipated", "difficulty passing stool"]),
  symptom("dry-stool", "Dry stool", "大便干", "inquiry", "Stool and urine", ["dry stools", "hard stool", "dry constipation"]),
  symptom("sticky-stool", "Sticky stool", "大便黏滞", "inquiry", "Stool and urine", ["sticky stools", "stool sticks", "unfinished stool"]),
  symptom("clear-urine", "Clear abundant urine", "小便清长", "inquiry", "Stool and urine", ["clear urine", "copious clear urine", "long clear urination"]),
  symptom("dark-urine", "Dark scanty urine", "小便短赤", "inquiry", "Stool and urine", ["dark urine", "scanty dark urine", "yellow urine"]),
  symptom("night-urine", "Frequent night urination", "夜尿频", "inquiry", "Stool and urine", ["nocturia", "wakes to urinate", "night urination"]),
  symptom("insomnia", "Insomnia", "失眠", "inquiry", "Sleep", ["poor sleep", "cannot sleep", "sleepless", "difficulty sleeping"]),
  symptom("dream-sleep", "Dream-disturbed sleep", "多梦", "inquiry", "Sleep", ["many dreams", "vivid dreams", "dream disturbed sleep"]),
  symptom("dizziness", "Dizziness", "头晕", "inquiry", "Head", ["dizzy", "lightheaded"]),
  symptom("tinnitus", "Tinnitus", "耳鸣", "inquiry", "Head", ["ringing in the ears", "ringing ears"]),
  symptom("dry-eyes", "Dry eyes", "目涩", "inquiry", "Head", ["eyes feel dry", "dry eye"]),
  symptom("lumbar-soreness", "Lumbar soreness", "腰酸", "inquiry", "Lumbar", ["sore lower back", "low back soreness", "lumbar ache", "back soreness", "sore back"]),
  symptom("knee-weakness", "Weak knees", "膝软", "inquiry", "Lumbar", ["knees feel weak", "sore knees", "knee weakness"]),
  symptom("fixed-pain", "Fixed stabbing pain", "刺痛固定", "inquiry", "Pain", ["stabbing pain", "fixed pain", "pain in one spot"]),
  symptom("palpitations", "Palpitations", "心悸", "inquiry", "Chest", ["heart racing", "palpitation", "aware of heartbeat"]),
  symptom("chest-oppression", "Chest oppression", "胸闷", "inquiry", "Chest", ["chest tightness", "chest feels tight", "oppressed chest"]),
  symptom("shortness-breath", "Shortness of breath", "气短", "inquiry", "Chest", ["short of breath", "breathless", "gets winded"]),
  symptom("cough", "Cough", "咳嗽", "inquiry", "Chest", ["coughing"]),
  symptom("clear-phlegm", "Copious clear phlegm", "痰清量多", "inquiry", "Chest", ["clear phlegm", "lots of clear sputum", "watery phlegm", "cough with clear phlegm"]),
  symptom("yellow-phlegm", "Sticky yellow phlegm", "痰黄黏", "inquiry", "Chest", ["yellow phlegm", "yellow sputum", "cough with yellow phlegm"]),
  symptom("delayed-period", "Delayed period", "月经后期", "inquiry", "Menstruation", ["late period", "period comes late", "delayed menses"]),
  symptom("early-period", "Early period", "月经先期", "inquiry", "Menstruation", ["period comes early", "early menses", "short cycle"]),
  symptom("scanty-pale-menses", "Scanty pale menses", "经少色淡", "inquiry", "Menstruation", ["light pale period", "scanty pale period", "pale scanty menses"]),
  symptom("dark-clots", "Dark menses with clots", "经色暗有血块", "inquiry", "Menstruation", ["dark clots", "period clots", "dark menstrual blood with clots"]),
  symptom("pain-eases-after-clots", "Pain eases after clots pass", "血块下后痛减", "inquiry", "Menstruation", ["pain better after clots", "pain eases when clots pass"]),
  symptom("cold-pain-better-warmth", "Cold pain relieved by warmth", "冷痛得温则减", "inquiry", "Menstruation", ["pain better with a hot water bottle", "cold pain better with warmth", "pain relieved by heat"]),
  symptom("bitter-taste", "Bitter taste", "口苦", "inquiry", "Diet", ["bitter mouth", "mouth tastes bitter"]),
  symptom("floating-pulse", "Floating pulse", "脉浮", "palpation", "Pulse", ["pulse is floating", "superficial pulse"]),
  symptom("deep-pulse", "Deep pulse", "脉沉", "palpation", "Pulse", ["pulse is deep", "deep pulses"]),
  symptom("slow-pulse", "Slow pulse", "脉迟", "palpation", "Pulse", ["pulse is slow", "slow pulses"]),
  symptom("rapid-pulse", "Rapid pulse", "脉数", "palpation", "Pulse", ["pulse is rapid", "fast pulse", "rapid pulses"]),
  symptom("wiry-pulse", "Wiry pulse", "脉弦", "palpation", "Pulse", ["pulse is wiry", "stringlike pulse", "wiry pulses"]),
  symptom("thin-pulse", "Thin pulse", "脉细", "palpation", "Pulse", ["pulse is thin", "thready pulse", "fine pulse", "thin pulses"]),
  symptom("weak-pulse", "Weak pulse", "脉弱", "palpation", "Pulse", ["pulse is weak", "forceless pulse", "weak pulses"]),
  symptom("slippery-pulse", "Slippery pulse", "脉滑", "palpation", "Pulse", ["pulse is slippery", "rolling pulse", "slippery pulses"]),
  symptom("choppy-pulse", "Choppy pulse", "脉涩", "palpation", "Pulse", ["pulse is choppy", "rough pulse", "choppy pulses"]),
  symptom("surging-pulse", "Surging pulse", "脉洪", "palpation", "Pulse", ["pulse is surging", "flooding pulse"]),
  symptom("soggy-pulse", "Soggy pulse", "脉濡", "palpation", "Pulse", ["pulse is soggy", "soft pulse"]),
  symptom("tight-pulse", "Tight pulse", "脉紧", "palpation", "Pulse", ["pulse is tight", "tight pulses"]),
  symptom("abdomen-cold", "Cold abdomen on palpation", "腹部按之凉", "palpation", "Abdomen", ["abdomen feels cold", "cold to the touch on the abdomen", "cold abdomen"]),
]

export const symptomById = new Map(symptoms.map((item) => [item.id, item]))

export const TONGUE_FIELDS = new Set(["Tongue body", "Tongue coat"])
export const PULSE_FIELDS = new Set(["Pulse"])

const bundles: { phrase: string; ids: string[] }[] = [
  { phrase: "cough with clear phlegm", ids: ["cough", "clear-phlegm"] },
  { phrase: "cough with yellow phlegm", ids: ["cough", "yellow-phlegm"] },
  { phrase: "pale swollen tongue", ids: ["swollen-tongue"] },
  { phrase: "yellow greasy coat", ids: ["yellow-greasy-coat"] },
  { phrase: "yellow greasy tongue coat", ids: ["yellow-greasy-coat"] },
]

export function parseSymptomText(raw: string): { ids: string[]; unrecognized: string[] } {
  let text = raw.toLowerCase().replace(/[，。；、]/g, ",").replace(/\s+/g, " ").trim()
  const found = new Set<string>()

  const phrases = [...bundles].sort((a, b) => b.phrase.length - a.phrase.length)
  for (const bundle of phrases) {
    let from = 0
    while (from < text.length) {
      const at = text.indexOf(bundle.phrase, from)
      if (at < 0) break
      if (bounded(text, at, bundle.phrase.length)) {
        for (const id of bundle.ids) found.add(id)
        text = blank(text, at, bundle.phrase.length)
      }
      from = at + bundle.phrase.length
    }
  }

  const aliasList: { alias: string; id: string }[] = []
  for (const item of symptoms) {
    for (const alias of item.aliases) {
      if (alias.trim().length < 2) continue
      aliasList.push({ alias, id: item.id })
    }
  }
  aliasList.sort((a, b) => b.alias.length - a.alias.length)

  for (const entry of aliasList) {
    let from = 0
    while (from < text.length) {
      const at = text.indexOf(entry.alias, from)
      if (at < 0) break
      if (bounded(text, at, entry.alias.length)) {
        found.add(entry.id)
        text = blank(text, at, entry.alias.length)
        from = at + entry.alias.length
      } else {
        from = at + 1
      }
    }
  }

  const unrecognized = text
    .split(/[^a-z0-9\u4e00-\u9fff]+/i)
    .map((token) => token.trim())
    .filter((token) => token.length >= 4)
    .filter((token) => !["with", "and", "the", "that", "this", "from", "have", "has", "been", "into", "after", "before", "during", "feels", "feeling"].includes(token))

  const uniqueUnknown = Array.from(new Set(unrecognized)).slice(0, 8)
  return { ids: Array.from(found), unrecognized: uniqueUnknown }
}

function bounded(text: string, start: number, length: number): boolean {
  const before = start === 0 ? " " : text[start - 1]
  const afterIndex = start + length
  const after = afterIndex >= text.length ? " " : text[afterIndex]
  return !isWordChar(before) && !isWordChar(after)
}

function isWordChar(char: string): boolean {
  return /[a-z0-9\u4e00-\u9fff]/i.test(char)
}

function blank(text: string, start: number, length: number): string {
  return text.slice(0, start) + " ".repeat(length) + text.slice(start + length)
}
