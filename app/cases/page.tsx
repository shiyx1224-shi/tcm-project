import type { Metadata } from "next"
import { CaseLibrary } from "@/components/case-library"

export const metadata: Metadata = {
  title: "Sample charts",
  description: "Teaching charts for kidney, stomach, menstrual, and holistic syndrome differentiation.",
}

export default function CasesPage() {
  return <CaseLibrary />
}
