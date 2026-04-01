"use client";

import { AlertCircle, Brain, Sparkles, Shield, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

type DisclaimerProps = {
  onAccept: () => void;
};

export default function Disclaimer({ onAccept }: DisclaimerProps) {
  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-2xl border border-blue-200/50 max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col items-center text-center mb-6">
        <div className="relative mb-4">
          <div className="p-4 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full shadow-lg">
            <Brain className="h-10 w-10 text-white" />
          </div>
          <Sparkles className="w-5 h-5 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
        </div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-700 bg-clip-text text-transparent mb-2">
          Meet Zoe
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl">
          Your empathetic AI companion, designed to provide a safe space for support and understanding
        </p>
      </div>

      {/* Important Notice */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5 mb-6">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-amber-100 rounded-lg">
            <AlertCircle className="h-5 w-5 text-amber-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-amber-800 mb-2">
              Important Information
            </h2>
            <p className="text-amber-700">
              Please read and understand these important points before continuing with Zoe.
            </p>
          </div>
        </div>
      </div>

      {/* Key Points */}
      <div className="space-y-4 mb-6">
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-5">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Brain className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-blue-800 mb-2">AI-Powered Support</h3>
              <p className="text-blue-700 text-sm">
                Zoe is an AI assistant under constant improvement for empathy and support.
                While designed to be helpful and understanding, responses are AI-generated and may not always be perfect.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 rounded-xl p-5">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-cyan-100 rounded-lg">
              <Shield className="h-4 w-4 text-cyan-600" />
            </div>
            <div>
              <h3 className="font-semibold text-cyan-800 mb-2">Professional Support</h3>
              <p className="text-cyan-700 text-sm">
                Zoe is not a replacement for professional mental health services.
                If you're experiencing a crisis or need immediate help, please contact a mental health professional or crisis service.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Heart className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-green-800 mb-2">Your Privacy Matters</h3>
              <p className="text-green-700 text-sm">
                Information you share helps personalize your experience with Zoe.
                Your conversations are treated with care and confidentiality.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Acknowledgment */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
        <p className="text-slate-700 font-medium text-center text-sm">
          By continuing, you acknowledge that you understand these limitations and agree to use Zoe as a supportive tool alongside, not instead of, professional care when needed.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row justify-center gap-3">
        <Button
          onClick={onAccept}
          className="bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white px-6 py-2.5 rounded-xl font-medium shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105"
        >
          I Understand - Continue to Zoe
        </Button>
        <Link href="/">
          <Button
            variant="outline"
            className="border-slate-300 text-slate-700 hover:bg-white px-6 py-2.5 rounded-xl font-medium transition-all duration-300"
          >
            Return to Homepage
          </Button>
        </Link>
      </div>
    </div>
  );
}
