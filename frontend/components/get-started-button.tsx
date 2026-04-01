"use client"

import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

export default function GetStartedButton() {
  const { isAuthenticated, isLoading, login } = useAuth()
  const router = useRouter()

  const handleClick = async () => {
    if (isLoading) return
    
    if (isAuthenticated) {
      // If already authenticated, go to landing page
      router.push("/")
    } else {
      // If not authenticated, trigger Keycloak login
      // After login, redirect to landing page
      await login(window.location.origin)
    }
  }

  return (
    <Button 
      className="bg-black hover:bg-gray-800 text-white px-8 py-4 rounded-full text-lg font-medium shadow-lg hover:shadow-black/25 transition-all duration-300 transform hover:scale-105"
      onClick={handleClick}
      disabled={isLoading}
    >
      {isLoading ? "Loading..." : "Get Started"}
    </Button>
  )
}

