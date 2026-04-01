'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { 
  Heart, 
  Brain, 
  Users, 
  Shield, 
  Sparkles, 
  ArrowRight,
  MessageCircle,
  Globe,
  Star,
  BookOpen,
  Award,
  HandHeart,
  CheckCircle,
  Quote,
  Zap,
  Target
} from 'lucide-react';

// Explore Features Button Component
function ExploreFeaturesButton() {
  const { isAuthenticated, isLoading, login } = useAuth();
  const router = useRouter();

  const handleClick = async () => {
    if (isLoading) return;
    
    if (isAuthenticated) {
      // If authenticated, go to healing rooms
      router.push("/healing-rooms");
    } else {
      // If not authenticated, trigger Keycloak login
      // After login, redirect to landing page
      await login(window.location.origin);
    }
  };

  return (
    <Button 
      className="bg-black hover:bg-gray-800 text-white px-8 py-4 rounded-full text-lg font-medium shadow-lg hover:shadow-black/25 transition-all duration-300 transform hover:scale-105"
      onClick={handleClick}
      disabled={isLoading}
    >
      {isLoading ? "Loading..." : "Explore Experimental Features"}
    </Button>
  );
}

export default function ModernLanding() {
  const [mounted, setMounted] = useState(false);

  const services = [
    {
      icon: Brain,
      title: "Inside our AI",
      description: "See how AI enhances our healing rooms, arts programs, and community initiatives with trauma-informed approaches."
    },
    {
      icon: Heart,
      title: "Healing Rooms",
      description: "Specialized spaces designed for trauma recovery and emotional wellbeing with AI-assisted support."
    },
    {
      icon: HandHeart,
      title: "Community Support",
      description: "Connect with others who understand your journey in a safe, moderated environment."
    }
  ];

  const steps = [
    {
      number: "1",
      title: "Discover"
    },
    {
      number: "2", 
      title: "Access"
    },
    {
      number: "3",
      title: "Experience"
    },
    {
      number: "4",
      title: "Thrive"
    }
  ];

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 md:px-12 lg:px-24">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center bg-gray-100 rounded-full px-4 py-2 mb-8">
            <span className="text-black font-medium text-sm tracking-wide uppercase">
              AI FOR HUMANITY
            </span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight text-gray-900">
            ThinkLife
          </h1>

          {/* Experimental Notice */}
          <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6 rounded-r-lg max-w-2xl mx-auto">
            <div className="flex items-start justify-center">
              <div className="flex-shrink-0">
                <Sparkles className="w-5 h-5 text-amber-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-semibold text-amber-900 mb-1">
                  Experimental Platform
                </p>
                <p className="text-sm text-amber-800">
                  Created by the Generative AI Engineers team at Think Round, Inc.
                </p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-4 mb-8 max-w-3xl mx-auto">
            <p className="text-lg text-gray-700 leading-relaxed">
              ThinkLife is currently used for <strong className="text-gray-900">local development and internal testing only</strong>. It serves as a sandbox environment to design, refine, and validate new AI-driven experiences before they are exposed to real users.
            </p>
            <p className="text-lg text-gray-700 leading-relaxed">
              This site showcases <strong className="text-gray-900">pre-release and beta versions</strong> of AI applications that are still under active development and review. Only the most stable, responsible, and impactful of these applications will move forward into the first public web release after formal approval from Think Round's leadership.
            </p>
          </div>

          {/* CTA Button */}
          <ExploreFeaturesButton />
        </div>
      </section>

      {/* About Section */}
      <section className="py-20 px-6 md:px-12 lg:px-24 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                About ThinkRound
              </h2>
              <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                We are a San Francisco-based nonprofit organization dedicated to creating ethical AI solutions 
                that prioritize human dignity and wellbeing.
              </p>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Through our Center for the Human Family, we're building bridges between diverse communities 
                and ensuring that AI development serves humanity's highest values.
              </p>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-black" />
                  <span className="text-gray-900">Nonprofit organization since 2004</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-black" />
                  <span className="text-gray-900">Trauma-informed AI development</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-black" />
                  <span className="text-gray-900">Community-centered approach</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-black" />
                  <span className="text-gray-900">Global impact through local action</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <Quote className="w-12 h-12 text-black mb-6" />
              <blockquote className="text-xl text-gray-900 italic mb-6">
                "Earth is home. Humans are family. AI for humanity."
              </blockquote>
              <p className="text-gray-600">
                This core belief guides everything we do at ThinkRound. We believe that technology should 
                serve humanity, not the other way around.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-20 px-6 md:px-12 lg:px-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Services
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              See how AI enhances our healing rooms, arts programs, and community initiatives.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 hover:shadow-lg transition-all duration-300 border border-gray-100">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <service.icon className="w-8 h-8 text-black" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">
                  {service.title}
                </h3>
                <p className="text-gray-600 text-center leading-relaxed">
                  {service.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-6 md:px-12 lg:px-24 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-black">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Getting started with ThinkLife is simple and personalized to your journey.
            </p>
          </div>

          <div className="relative">
            {/* Steps Container */}
            <div className="flex flex-col lg:flex-row items-center justify-center space-y-16 lg:space-y-0 lg:space-x-16">
              {steps.map((step, index) => (
                <div key={index} className="flex flex-col lg:flex-row items-center">
                  {/* Step Card */}
                  <div className="text-center">
                    <div className="relative group mb-6">
                      {/* Animated Circle Background */}
                      <div className="w-24 h-24 mx-auto rounded-full bg-black flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-all duration-300">
                        <div className="absolute inset-0 rounded-full bg-black animate-pulse opacity-75"></div>
                        <span className="text-2xl font-bold text-white relative z-10">
                          {step.number}
                        </span>
                      </div>
                      
                      {/* Floating Animation Effect */}
                      <div className="absolute inset-0 rounded-full border-2 border-gray-200 animate-[ping_2s_ease-in-out_infinite]"></div>
                    </div>
                    
                    <h3 className="text-xl md:text-2xl font-bold text-black tracking-wide uppercase">
                      {step.title}
                    </h3>
                  </div>

                  {/* Modern Animated Flow Arrow - Only show between steps */}
                  {index < steps.length - 1 && (
                    <>
                      {/* Desktop Flow Arrow */}
                      <div className="hidden lg:flex mx-12 items-center">
                        <div className="relative flex items-center">
                          {/* Flowing Dots Animation */}
                          <div className="flex space-x-2">
                            {[0, 1, 2, 3, 4].map((dotIndex) => (
                              <div
                                key={dotIndex}
                                className="w-2 h-2 rounded-full bg-black"
                                style={{
                                  animation: `flowDots 2s ease-in-out infinite ${dotIndex * 0.2}s`
                                }}
                              ></div>
                            ))}
                          </div>
                          
                          {/* Arrow Head */}
                          <div className="ml-2">
                            <svg
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              fill="none"
                              className="transform animate-bounce"
                            >
                              <path
                                d="M13.025 1l-2.847 2.828 6.176 6.176h-16.354v3.992h16.354l-6.176 6.176 2.847 2.828 10.975-11z"
                                fill="black"
                              />
                            </svg>
                          </div>
                        </div>
                      </div>

                      {/* Mobile Flow Arrow */}
                      <div className="lg:hidden my-8 flex flex-col items-center">
                        <div className="relative flex flex-col items-center">
                          {/* Vertical Flowing Dots */}
                          <div className="flex flex-col space-y-2">
                            {[0, 1, 2, 3].map((dotIndex) => (
                              <div
                                key={dotIndex}
                                className="w-2 h-2 rounded-full bg-black"
                                style={{
                                  animation: `flowDotsVertical 2s ease-in-out infinite ${dotIndex * 0.2}s`
                                }}
                              ></div>
                            ))}
                          </div>
                          
                          {/* Downward Arrow */}
                          <div className="mt-2">
                            <svg
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              fill="none"
                              className="transform animate-bounce"
                            >
                              <path
                                d="M1 13.025l2.828-2.847 6.176 6.176v-16.354h3.992v16.354l6.176-6.176 2.828 2.847-11 10.975z"
                                fill="black"
                              />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <style jsx>{`
          @keyframes flowDots {
            0% {
              opacity: 0.3;
              transform: scale(0.8);
            }
            50% {
              opacity: 1;
              transform: scale(1.2);
            }
            100% {
              opacity: 0.3;
              transform: scale(0.8);
            }
          }
          
          @keyframes flowDotsVertical {
            0% {
              opacity: 0.3;
              transform: scale(0.8);
            }
            50% {
              opacity: 1;
              transform: scale(1.2);
            }
            100% {
              opacity: 0.3;
              transform: scale(0.8);
            }
          }
        `}</style>
      </section>

      {/* Community Section */}
      <section className="py-20 px-6 md:px-12 lg:px-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Join Our Community
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Connect with others who are on their journey to healing and personal growth.
            </p>
          </div>

          <div className="max-w-4xl mx-auto text-center">
            <ExploreFeaturesButton />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-6 md:px-12 lg:px-24 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-gray-600">
              Common questions about how we integrate AI into our programs.
            </p>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                What makes ThinkLife different from other AI platforms?
              </h3>
              <p className="text-gray-600">
                We prioritize trauma-informed care and human-centered design in everything we do. Our AI systems 
                are built with safety, empathy, and cultural sensitivity at their core.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Is the platform suitable for people with trauma histories?
              </h3>
              <p className="text-gray-600">
                Yes, our entire platform is designed with trauma-informed principles. We provide safe spaces, 
                clear consent processes, and resources for when difficult emotions arise.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                How does Zoe, your AI companion, work?
              </h3>
              <p className="text-gray-600">
                Zoe is trained in trauma-informed communication and provides empathetic support 24/7. She's designed 
                to be a supportive presence while always encouraging connection with human support when needed.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Is ThinkLife free to use?
              </h3>
              <p className="text-gray-600">
                Yes, our core services are free to use. We're a nonprofit organization committed to making 
                AI-enhanced healing and creative experiences accessible to everyone.
              </p>
            </div>
          </div>
        </div>
      </section>


    </div>
  );
} 