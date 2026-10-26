import { Suspense } from "react"
import { DeskGate } from "@/components/desk-gate"

export default function Page() {
  return (
    <Suspense fallback={<p className="px-4 py-8 text-sm text-muted-foreground">Opening the chart…</p>}>
      <DeskGate />
    </Suspense>
  )
}
