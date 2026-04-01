"use client"

import { ReactNode } from "react"
import { KeycloakProvider } from "@/contexts/KeycloakContext"

interface Props {
  children: ReactNode
}

export default function AuthSessionProvider({ children }: Props) {
  return (
    <KeycloakProvider>
      {children}
    </KeycloakProvider>
  )
}
