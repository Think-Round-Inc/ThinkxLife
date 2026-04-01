'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Sparkles, Brain, Zap, Globe, Users, Shield } from 'lucide-react';

export default function ModernHero() {
  const [mounted, setMounted] = useState(false);
  const [currentFeature, setCurrentFeature] = useState(0);

  const features = [
    { icon: Brain, text: 'AI-Powered Insights' },
    { icon: Shield, text: 'Ethical AI Practices' },
    { icon: Users, text: 'Community Engagement' },
    { icon: Globe, text: 'Global Impact' },
  ];

  useEffect(() => {
    setMounted(true);
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [features.length]);

  if (!mounted) return null;

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-100 via-purple-100 to-blue-50 pt-8">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-200/40 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-purple-200/20 to-blue-200/15 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-purple-300/30 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          ></div>
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-12 lg:px-24 text-center">
        {/* Welcome Badge */}
        <div className="inline-flex items-center gap-2 bg-white/60 backdrop-blur-sm border border-purple-200/50 rounded-full px-6 py-3 mb-6 animate-fade-in shadow-lg">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <span className="text-purple-800 font-medium">Sail the Seas of ThinkLife</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 bg-gradient-to-r from-slate-800 via-purple-700 to-blue-700 bg-clip-text text-transparent animate-fade-in-up leading-tight">
          Earth is home.
          <br />
          <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Humans are family.
          </span>
          <br />
          <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI for humanity.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed animate-fade-in-up delay-200 mb-16">
          At ThinkRound, Inc, we're pioneering AI for humanity through ThinkLife, our comprehensive platform
          that integrates AI thoughtfully into healing rooms, arts programs, and community initiatives while preserving human dignity and cultural authenticity.
        </p>

        {/* Rotating Features */}
        <div className="mb-12 animate-fade-in-up delay-300">
          <div className="inline-flex items-center gap-3 bg-white/50 backdrop-blur-sm border border-purple-200/30 rounded-2xl px-8 py-4 shadow-lg">
            {features.map((Feature, index) => (
              <div
                key={index}
                className={`flex items-center gap-2 transition-all duration-500 ${
                  index === currentFeature
                    ? 'text-purple-700 scale-110'
                    : 'text-slate-500 scale-90'
                }`}
              >
                <Feature.icon className="w-6 h-6" />
                <span className="font-medium">{Feature.text}</span>
                {index < features.length - 1 && (
                  <div className="w-px h-6 bg-purple-200 ml-4"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-purple-400/50 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-purple-500/70 rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>

      <style jsx>{`

        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        @keyframes spin-slow {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes fade-in-up {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
        .animate-fade-in {
          animation: fade-in 1s ease-out;
        }
        .animate-fade-in-up {
          animation: fade-in-up 1s ease-out;
        }
        .delay-200 {
          animation-delay: 0.2s;
        }
        .delay-300 {
          animation-delay: 0.3s;
        }
        .delay-400 {
          animation-delay: 0.4s;
        }
        .delay-500 {
          animation-delay: 0.5s;
        }
                .delay-1000 {
          animation-delay: 1s;
        }
      `}</style>
    </section>
  );
}
