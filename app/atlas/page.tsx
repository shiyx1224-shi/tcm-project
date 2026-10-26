import type { Metadata } from "next"
import { AtlasView } from "@/components/atlas-view"

export const metadata: Metadata = {
  title: "Pattern atlas",
  description: "Key signs, contradicting signs, and teaching-set co-occurrence for each syndrome pattern.",
}

export default function AtlasPage() {
  return <AtlasView />
}
