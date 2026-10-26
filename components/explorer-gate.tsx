"use client"

import { useSearchParams } from "next/navigation"
import { SyndromeExplorer } from "@/components/syndrome-explorer"

export function ExplorerGate() {
  const params = useSearchParams()
  const caseId = params.get("case")
  const tab = params.get("tab")
  const panel = tab === "atlas" ? "atlas" : "chart"
  return <SyndromeExplorer key={`${caseId ?? "blank"}-${panel}`} initialCaseId={caseId} initialPanel={panel} />
}
