import { Suspense } from "react"
import { ExplorerGate } from "@/components/explorer-gate"

export default function ExplorerPage() {
  return (
    <Suspense fallback={<p className="px-4 py-8 text-sm text-muted-foreground">Opening the explorer…</p>}>
      <ExplorerGate />
    </Suspense>
  )
}
