"use client"

import { useSearchParams } from "next/navigation"
import { ConsultDesk } from "@/components/consult-desk"

export function DeskGate() {
  const params = useSearchParams()
  const caseId = params.get("case")
  return <ConsultDesk key={caseId ?? "blank"} initialCaseId={caseId} />
}
