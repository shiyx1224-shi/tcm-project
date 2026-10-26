"use client"

import { useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"

/** Keeps old `/?case=` links working without making the home route dynamic. */
export function CaseRedirect() {
  const router = useRouter()
  const params = useSearchParams()
  const caseId = params.get("case")

  useEffect(() => {
    if (!caseId) return
    router.replace(`/explorer?case=${encodeURIComponent(caseId)}`)
  }, [caseId, router])

  return null
}
