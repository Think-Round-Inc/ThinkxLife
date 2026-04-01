"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { Loader2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function CallbackPage() {
  const { isAuthenticated, isLoading, login } = useAuth()
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check for errors in URL hash (Keycloak uses hash fragments)
    const hash = window.location.hash.substring(1) // Remove #
    const hashParams = new URLSearchParams(hash)
    const errorParam = hashParams.get('error')
    
    if (errorParam) {
      console.error('Keycloak authentication error:', errorParam)
      setError(errorParam)
      
      // If it's a login_required error, try to login again
      if (errorParam === 'login_required') {
        // Clear the error from URL
        window.history.replaceState({}, document.title, window.location.pathname)
        // Wait a moment for state to clear, then retry login
        setTimeout(async () => {
          await login(window.location.origin)
        }, 500)
        return
      }
      
      // For other errors, show error message and redirect to signin
      setTimeout(() => {
        router.push('/auth/signin')
      }, 3000)
      return
    }

    // If there's a hash with tokens, Keycloak is processing the callback
    // Wait for Keycloak to finish processing before checking auth status
    if (hash && !errorParam) {
      // Keycloak is processing tokens - wait a bit
      const timer = setTimeout(() => {
        if (isAuthenticated) {
          // Get redirect URI from localStorage or default to landing page
          const savedRedirect = localStorage.getItem('keycloak_redirect_uri') || window.location.origin
          localStorage.removeItem('keycloak_redirect_uri')
          router.push(savedRedirect)
        } else if (!isLoading) {
          // If still not authenticated after processing, go to signin
          router.push('/auth/signin')
        }
      }, 1000)
      return () => clearTimeout(timer)
    }

    // If no hash and no error, check authentication status normally
    if (!isLoading) {
      if (isAuthenticated) {
        // Get redirect URI from localStorage or default to landing page
        const savedRedirect = localStorage.getItem('keycloak_redirect_uri') || window.location.origin
        localStorage.removeItem('keycloak_redirect_uri')
        router.push(savedRedirect)
      } else {
        // Wait a bit for Keycloak to process
        const timer = setTimeout(() => {
          if (!isAuthenticated) {
            router.push('/auth/signin')
          }
        }, 2000)
        return () => clearTimeout(timer)
      }
    }
  }, [isAuthenticated, isLoading, router, login])

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-purple-100 to-blue-50 p-6">
        <div className="w-full max-w-md rounded-2xl bg-white/90 backdrop-blur-md shadow-xl border border-purple-200/50 p-8 space-y-6">
          <div className="flex items-center justify-center">
            <AlertCircle className="w-12 h-12 text-amber-600" />
          </div>
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold text-gray-900">Authentication Error</h2>
            <p className="text-gray-600">
              {error === 'login_required' 
                ? 'Please complete the login process.' 
                : `An error occurred: ${error}`}
            </p>
            {error === 'login_required' && (
              <p className="text-sm text-gray-500 mt-2">Redirecting to login...</p>
            )}
          </div>
          {error !== 'login_required' && (
            <Button
              className="w-full bg-black hover:bg-gray-800 text-white"
              onClick={() => router.push('/auth/signin')}
            >
              Go to Sign In
            </Button>
          )}
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-purple-100 to-blue-50">
      <div className="text-center space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600 mx-auto" />
        <p className="text-slate-600">Completing authentication...</p>
      </div>
    </main>
  )
}

