"use client";

import { Button } from "@/components/ui/button";
import { Brain, Sparkles, MessageCircle, Heart, Shield, Lightbulb, AlertTriangle, Mail, Phone } from "lucide-react";

type AceResultsProps = {
  score: number;
  userName: string;
  onStartChat: () => void;
};

export default function AceResults({ score, userName, onStartChat }: AceResultsProps) {
  const isHighScore = score >= 4;
  
  const getResultContent = () => {
    if (isHighScore) {
      return {
        title: "Your Journey Continues",
        message: "Thank you for sharing your experiences with us. Based on your responses, we have specific recommendations for your support.",
        icon: "🤝",
        color: "from-blue-50 to-indigo-50",
        borderColor: "border-blue-200"
      };
    } else {
      return {
        title: "Your Journey Continues",
        message: "Thank you for sharing your experiences with us. You have options to continue your journey with either chat support or our specialized training program.",
        icon: "🌞",
        color: "from-green-50 to-emerald-50",
        borderColor: "border-green-200"
      };
    }
  };

  const resultData = getResultContent();

  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-2xl border border-blue-200/50 max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col items-center text-center mb-6">
        <div className="relative mb-4">
          <div className="p-3 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full shadow-lg">
            <Brain className="h-10 w-10 text-white" />
          </div>
          <Sparkles className="w-5 h-5 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
        </div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-blue-700 bg-clip-text text-transparent mb-2">
          Questionnaire Complete
        </h2>
        <p className="text-sm text-slate-600 max-w-2xl">
          Thank you for sharing, {userName}. Here's what this means for our conversations.
        </p>
      </div>

      {/* Score Display */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6 mb-6 shadow-lg">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-slate-800 mb-2">Your ACE Score</h3>
          <div className="text-4xl font-bold text-blue-600 mb-2">{score}</div>
          <p className="text-slate-600 text-sm">out of 10</p>
        </div>
      </div>

      {/* Results Card */}
      <div className={`bg-gradient-to-r ${resultData.color} ${resultData.borderColor} border rounded-2xl p-6 mb-6 shadow-lg`}>
        <div className="flex items-start gap-4">
          <div className="text-3xl">{resultData.icon}</div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-slate-800 mb-3">{resultData.title}</h3>
            <p className="text-slate-700 text-sm leading-relaxed mb-4">
              {resultData.message}
            </p>
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-white/40">
              <p className="text-slate-700 font-medium text-sm">
                {isHighScore 
                  ? `${userName}, we believe specialized support would be most beneficial for your journey. Our team is here to help you access the right resources.`
                  : `Thank you for trusting me with your story, ${userName}. You have options to move forward in the way that feels right for you.`
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {isHighScore ? (
        /* High Score (>= 4) - Combined Professional Support Container */
        <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="p-2 bg-orange-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-orange-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-orange-800 mb-3">Professional Support Recommended</h3>
              <p className="text-orange-700 text-sm leading-relaxed mb-4">
                Based on your ACE score, we strongly recommend connecting with our specialized support team 
                to learn more about our Trauma Transformation Training program. This program is specifically 
                designed to help individuals with similar experiences.
              </p>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-white/40 mb-4">
                <h4 className="font-semibold text-orange-800 mb-3">Contact Information:</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-orange-600" />
                    <a 
                      href="mailto:info@thinkround.org" 
                      className="text-orange-700 hover:text-orange-800 font-medium underline"
                    >
                      info@thinkround.org
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center pt-4 border-t border-orange-200/50">
            <p className="text-orange-700 text-sm mb-4 font-medium">
              Chat functionality is currently unavailable for your safety and to ensure you receive the most appropriate support.
            </p>
            <Button
              disabled
              className="bg-gray-400 text-white py-3 px-6 rounded-2xl font-semibold cursor-not-allowed opacity-60"
            >
              <MessageCircle className="w-5 h-5 mr-2" />
              Chat Unavailable
            </Button>
          </div>
        </div>
      ) : (
        /* Low Score (< 4) - Chat Option and Training Option */
        <>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="p-1.5 bg-green-100 rounded-lg">
                  <MessageCircle className="h-4 w-4 text-green-600" />
                </div>
                <h4 className="font-semibold text-green-800 text-sm">Chat with Zoe</h4>
              </div>
              <p className="text-green-700 text-xs">
                Continue with our AI companion for supportive conversations tailored to your experiences.
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="p-1.5 bg-blue-100 rounded-lg">
                  <Heart className="h-4 w-4 text-blue-600" />
                </div>
                <h4 className="font-semibold text-blue-800 text-sm">Trauma Transformation Training</h4>
              </div>
              <p className="text-blue-700 text-xs">
                Learn more about our specialized training program designed for healing and growth.
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={onStartChat}
              className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white py-4 px-8 rounded-2xl font-semibold shadow-lg hover:shadow-green-500/25 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 active:scale-95 min-h-[48px]"
            >
              <MessageCircle className="w-5 h-5 mr-2" />
              Start Chat with Zoe
            </Button>
            
            <Button
              onClick={() => window.open('mailto:info@thinkround.org?subject=Trauma Transformation Training Inquiry', '_blank')}
              variant="outline"
              className="border-2 border-blue-500 text-blue-600 hover:bg-blue-50 hover:border-blue-600 py-4 px-8 rounded-2xl font-semibold shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 active:scale-95 min-h-[48px]"
            >
              <Mail className="w-5 h-5 mr-2" />
              Learn About Training
            </Button>
          </div>
          
          <p className="text-slate-500 mt-4 text-sm text-center">
            Choose the support option that feels right for your journey
          </p>
        </>
      )}
    </div>
  );
}
