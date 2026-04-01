"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Loader2, Sparkles, Shield, Heart, Brain } from "lucide-react"
import Link from "next/link"

export default function SignInPage() {
  const { isAuthenticated, isLoading, login, register } = useAuth()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (isAuthenticated && !isLoading && mounted) {
      router.push("/")
    }
  }, [isAuthenticated, isLoading, mounted, router])

  const handleLogin = async () => {
    await login(window.location.origin)
  }

  const handleRegister = async () => {
    await register(window.location.origin)
  }

  if (!mounted) {
    return null
  }

  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-gray-50 p-6">
        <div className="w-full max-w-md rounded-2xl bg-white shadow-xl border border-gray-200 p-8 space-y-6">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Loader2 className="w-8 h-8 animate-spin text-black" />
            <p className="text-center text-gray-600">Connecting to ThinkLife...</p>
          </div>
        </div>
      </main>
    )
  }

  if (isAuthenticated) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-gray-50 p-6">
        <div className="w-full max-w-md rounded-2xl bg-white shadow-xl border border-gray-200 p-8 space-y-6">
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <Shield className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">
              Already Signed In
            </h1>
            <p className="text-gray-600">Redirecting to your chat...</p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-gray-50 p-6">
      <div className="w-full max-w-md">
        {/* Logo and Branding */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center justify-center mb-6">
            <span className="text-2xl font-bold tracking-wider text-black">
              ThinkLife
              <sup className="text-xs font-normal text-gray-700 ml-2 tracking-normal flex items-center justify-center">
                from <img src="/tr_logo.png" alt="Think Round" className="w-3 h-3 ml-1" /> Think Round, Inc
              </sup>
            </span>
          </Link>
          <div className="inline-flex items-center bg-gray-100 rounded-full px-4 py-2 mb-4">
            <span className="text-black font-medium text-sm tracking-wide uppercase">
              AI FOR HUMANITY
            </span>
          </div>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl bg-white shadow-xl border border-gray-200 p-8 space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome to ThinkLife
            </h1>
            <p className="text-gray-600">
              Sign in to continue your journey with AI-powered support
            </p>
          </div>

          {/* Features Icons */}
          <div className="flex items-center justify-center gap-6 py-4 border-y border-gray-100">
            <div className="flex flex-col items-center gap-2">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Brain className="w-5 h-5 text-black" />
              </div>
              <span className="text-xs text-gray-600">AI Support</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Heart className="w-5 h-5 text-black" />
              </div>
              <span className="text-xs text-gray-600">Trauma-Informed</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Shield className="w-5 h-5 text-black" />
              </div>
              <span className="text-xs text-gray-600">Safe Space</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button 
              className="w-full bg-black hover:bg-gray-800 text-white py-6 text-base font-medium shadow-lg hover:shadow-black/25 transition-all duration-300 transform hover:scale-[1.02] active:scale-100" 
              onClick={handleLogin}
            >
              Sign In
            </Button>
            <Button 
              className="w-full border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 text-gray-900 py-6 text-base font-medium transition-all duration-300" 
              variant="outline"
              onClick={handleRegister}
            >
              Create Account
            </Button>
          </div>

          {/* Info Text */}
          <div className="pt-4 border-t border-gray-100">
            <p className="text-center text-xs text-gray-500">
              By continuing, you agree to use ThinkLife responsibly and in accordance with our trauma-informed principles.
            </p>
          </div>
        </div>

        {/* Footer Link */}
        <div className="mt-6 text-center">
          <Link 
            href="/" 
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            ← Back to Home
          </Link>
        </div>
      </div>
    </main>
  )
}
