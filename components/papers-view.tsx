import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const papers = [
  {
    tag: "Multi-label, small charts",
    title: "Syndrome differentiation with a multi-label deep forest",
    citation: "Gong, Jiang, Chen, and Qi. Frontiers in Genetics, 2023.",
    href: "https://doi.org/10.3389/fgene.2023.1272016",
    points: [
      "A patient can carry more than one syndrome. Turning that into a single class throws away the combination, which is common in kidney and stomach charts.",
      "TCM case collections are small, uneven, and full of synonymous symptom names. The paper standardizes names, then selects features with a Pearson-adjusted multi-label Relief method before a deep forest.",
      "The metrics that matter are set-based: Hamming loss, one-error, coverage, ranking loss, and average precision, not a single accuracy.",
    ],
    here: "The desk keeps every pattern that clears the line, standardizes free text into one symptom dictionary, and reports the same family of multi-label metrics in the teaching lab. The live score stays readable instead of training a deep forest on data we do not have.",
  },
  {
    tag: "Sparse four examinations",
    title: "Cross features for high-dimensional symptom fields",
    citation: "Huang, Miao, Chen, Zhong, Yang, Ma, and Wen. JMIR Medical Informatics, 2022.",
    href: "https://doi.org/10.2196/29290",
    points: [
      "Real charts are sparse. Tongue, voice, or pulse is often missing, and a flat vector of symptoms hides which signs sit in the same diagnostic field.",
      "The paper structures dysmenorrhea records by the four examinations, embeds each field, and learns both linear crosses and local convolutional crosses. Nine syndrome classes are the target.",
      "Their reported accuracy is on a curated dysmenorrhea corpus. It is not a number this desk can claim.",
    ],
    here: "Intake is grouped by inspection, listening and smelling, inquiry, and palpation. Empty tongue or pulse is called out and slightly discounts coverage. Named crosses, such as purple tongue with a choppy pulse, boost the patterns that cross is known to support.",
  },
  {
    tag: "Holistic, not one disease",
    title: "BERT and a convolutional net with syndrome constraints",
    citation: "Chen, Zhang, Liu, Wang, Jin, Yang, and Zhang. Integrative Medicine Research, 2024.",
    href: "https://doi.org/10.1016/j.imr.2023.101019",
    points: [
      "Most models learn syndromes inside one disease. Holistic differentiation asks which principles, organs, and pathologies are present across diseases, and several of those labels co-exist.",
      "The paper constrains exterior against interior, and deficiency against excess, while other syndromes can fire together through a sigmoid-style head.",
      "A symptom correlation view checks whether the model noticed the signs a pattern is supposed to hang on.",
    ],
    here: "The holistic lens scores principles, organs, and pathologies together. Competing pairs are damped so the leader pulls ahead without erasing a close second. The atlas shows how key signs co-occur inside each pattern on the teaching charts.",
  },
]

export function PapersView() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
      <div>
        <p className="text-xs tracking-[0.18em] text-primary uppercase">Parent papers</p>
        <h1 className="font-heading mt-1 text-3xl tracking-tight">Three ways of reading the same clinical task</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          Syndrome differentiation takes signs from the four examinations and returns one or more patterns. The three studies disagree about the model, and they agree about the obstacles: labels co-exist, charts are sparse or small, and a model trained inside one disease misses the holistic reading.
        </p>
      </div>

      {papers.map((paper) => (
        <Card key={paper.href}>
          <CardHeader>
            <p className="text-xs tracking-wide text-primary uppercase">{paper.tag}</p>
            <CardTitle className="font-heading text-2xl">{paper.title}</CardTitle>
            <p className="text-sm text-muted-foreground">{paper.citation}</p>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-relaxed">
            <ul className="list-disc space-y-2 pl-4">
              {paper.points.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
            <p>
              <span className="font-medium">On this desk. </span>
              {paper.here}
            </p>
            <a className="text-primary underline-offset-4 hover:underline" href={paper.href}>
              {paper.href.replace("https://", "")}
            </a>
          </CardContent>
        </Card>
      ))}

      <Card>
        <CardHeader>
          <CardTitle>What this project does not do</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-relaxed text-muted-foreground">
          <p>
            It does not retrain their forests, convolutional nets, or BERT model, and it does not reuse their hospital or guideline corpora. Kidney, stomach, and dysmenorrhea names follow the pattern families those papers study. The symptom profiles are standard teaching distinctions, written for this desk.
          </p>
          <p>
            It does not prescribe herbs, formulas, or doses. A pattern name is a classification, not a treatment plan. Anyone making a clinical decision needs a qualified practitioner and, where it is relevant, biomedical care.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
