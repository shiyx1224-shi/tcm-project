import type { Metadata } from "next"
import { PapersView } from "@/components/papers-view"

export const metadata: Metadata = {
  title: "Parent papers",
  description: "How the syndrome workbench uses three TCM machine-learning papers.",
}

export default function PapersPage() {
  return <PapersView />
}
