import { redirect } from "next/navigation"

export default function AtlasRedirect() {
  redirect("/explorer?tab=atlas")
}
