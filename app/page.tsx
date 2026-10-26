import { Suspense } from "react"
import { CaseRedirect } from "@/components/case-redirect"
import { HomeLanding } from "@/components/home-landing"

export default function Page() {
  return (
    <>
      <Suspense fallback={null}>
        <CaseRedirect />
      </Suspense>
      <HomeLanding />
    </>
  )
}
