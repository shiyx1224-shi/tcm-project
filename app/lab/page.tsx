import type { Metadata } from "next"
import { LabView } from "@/components/lab-view"

export const metadata: Metadata = {
  title: "Teaching lab",
  description: "Multi-label metrics for the pattern ranker, an overlap baseline, and ML-KNN on the teaching set.",
}

export default function LabPage() {
  return <LabView />
}
