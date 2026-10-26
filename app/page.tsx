import { HomeLanding } from "@/components/home-landing"
import { redirect } from "next/navigation"

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ case?: string }>
}) {
  const params = await searchParams
  if (params.case) {
    redirect(`/explorer?case=${encodeURIComponent(params.case)}`)
  }
  return <HomeLanding />
}
