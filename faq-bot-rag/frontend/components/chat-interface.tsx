"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Send, 
  User, 
  Volume2, 
  Heart,
  Play,
  Settings,
  RotateCcw,
  MessageSquare
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { getUserInfo } from "../lib/keycloak";

// Import sub-components
import AgeRestriction from "./age-restriction";
import Disclaimer from "./disclaimer";
import UserInfoForm from "./user-info-form";
import AceQuestionnaire from "./ace-questionnaire";
import AceResults from "./ace-results";

// Types
interface UserInfo {
  name: string;
  age: number | null;
  email?: string;
}

type Answer = "yes" | "no" | "skip" | null;

interface Message {
  id: string;
  content: string;
  sender: "user" | "zoe";
  timestamp: Date;
  expression?: string;
}

interface ChatInterfaceProps {
  className?: string;
  variant?: "healing-rooms" | "general" | "ai-awareness";
  showSteps?: boolean;
  initialStep?: "disclaimer" | "userInfo" | "questionnaire" | "results" | "chat" | "ageRestriction";
}

export default function ChatInterface({ 
  className = "",
  variant = "general",
  showSteps = true,
  initialStep = "disclaimer"
}: ChatInterfaceProps) {
  const [step, setStep] = useState<
    | "disclaimer"
    | "userInfo"
    | "questionnaire"
    | "results"
    | "chat"
    | "ageRestriction"
  >(showSteps ? initialStep : "chat");
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [aceScore, setAceScore] = useState<number>(0);
  const [aceAnswers, setAceAnswers] = useState<Answer[]>([]);
  const [aceDetails, setAceDetails] = useState<string[]>([]);

  // Chat states
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [avatarMode, setAvatarMode] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const [userId] = useState<string>(() => {
    // Generate a unique user ID that persists for the session
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null);

  // Auto-scroll to bottom when messages change or loading state changes
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end'
      });
    }
  }, [messages, isLoading]);

  // Age restriction handler (not used since AgeRestriction doesn't take props)
  const handleAgeRestriction = () => {
    // This component doesn't actually handle age confirmation
    // It just shows a restriction message
  };

  // Disclaimer handler
  const handleDisclaimerAccept = () => {
    setStep("userInfo");
  };

  // User info handler
  const handleUserInfoSubmit = (info: UserInfo) => {
    setUserInfo(info);
    setStep("questionnaire");
  };

  // ACE questionnaire handler
  const handleQuestionnaireComplete = (score: number, answers: Answer[], details: string[]) => {
    setAceAnswers(answers);
    setAceScore(score);
    setAceDetails(details);
    setStep("results");
  };

  // Get auth state
  const { isAuthenticated, isLoading: authLoading, login } = useAuth();
  
  // Get Keycloak user info for autofill
  const [keycloakUserInfo, setKeycloakUserInfo] = useState<{
    firstName?: string;
    lastName?: string;
    name?: string;
  } | null>(null);
  
  useEffect(() => {
    // Get user info from Keycloak if authenticated
    if (isAuthenticated) {
      const userInfo = getUserInfo();
      if (userInfo) {
        setKeycloakUserInfo({
          firstName: userInfo.firstName || undefined,
          lastName: userInfo.lastName || undefined,
          name: userInfo.name || undefined,
        });
      }
    }
  }, [isAuthenticated]);

  // Results handler - requires authentication before starting chat
  const handleStartChat = () => {
    // Prevent chat access for high ACE scores (>= 4)
    if (aceScore >= 4) {
      console.warn('Chat access denied for ACE score >= 4');
      return;
    }
    
    // Check if user is authenticated
    if (!authLoading && !isAuthenticated) {
      // Trigger Keycloak login, redirect back to landing page after authentication
      // User can then navigate to healing rooms or chat from there
      (async () => {
        await login(window.location.origin);
      })();
      return;
    }
    
    // If authenticated, proceed to chat
    setStep("chat");
    // Clear any existing session to start fresh
    setSessionId(null);
    sessionIdRef.current = null;
    setMessages([]);
    // Initialize chat with personalized message
    const initialMessage = getInitialMessage();
    setMessages([{
      id: "1",
      content: initialMessage,
      sender: "zoe",
      timestamp: new Date(),
      expression: "caring"
    }]);
  };

  const getInitialMessage = () => {
    if (aceScore <= 3) {
      return `Hey ${userInfo?.name || 'there'}! I'm Zoe, an AI companion here to support you.

Let me be transparent about our interaction:

I am an AI assistant, not a human:
• I cannot diagnose, treat, or provide professional therapy for mental health conditions

How I can support you:
• Provide empathetic, non-judgmental conversation and active listening
• Share general wellness information and coping strategies
• Offer a safe space for reflection and processing your thoughts

I'm here to listen and support you. What's on your mind today?`;
    } else if (aceScore <= 6) {
      return `Hello ${userInfo?.name || 'strong spirit'}! I'm Zoe, an AI companion here to support you.

Let me be transparent about our interaction:

I am an AI assistant, not a human:
• I cannot diagnose, treat, or provide professional therapy for mental health conditions

How I can support you:
• Provide empathetic, non-judgmental conversation and active listening
• Share general wellness information and coping strategies
• Offer a safe space for reflection and processing your thoughts

I'm here to listen and support you. What's on your mind today?`;
    } else {
      return `Hi ${userInfo?.name || 'friend'}!I'm Zoe, an AI companion here to support you.

Let me be transparent about our interaction:

I am an AI assistant, not a human:
• I cannot diagnose, treat, or provide professional therapy for mental health conditions

How I can support you:
• Provide empathetic, non-judgmental conversation and active listening
• Share general wellness information and coping strategies
• Offer a safe space for reflection and processing your thoughts

I'm here to listen and support you. What's on your mind today?`;
    }
    // Since scores >= 4 can't access chat, we only need to handle scores < 4
    return `Hey ${userInfo?.name || 'there'}! What can we explore together today?`;
  };

  // Expression analysis
  const analyzeExpression = (text: string): string => {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('sorry') || lowerText.includes('understand') || lowerText.includes('difficult')) {
      return 'empathetic';
    } else if (lowerText.includes('great') || lowerText.includes('wonderful') || lowerText.includes('amazing')) {
      return 'happy';
    } else if (lowerText.includes('question') || lowerText.includes('think') || lowerText.includes('consider')) {
      return 'thoughtful';
    } else if (lowerText.includes('hello') || lowerText.includes('hi ') || lowerText.includes('welcome')) {
      return 'welcoming';
    }
    
    return 'caring';
  };

  // TTS functionality
  const speakMessage = async (audioData: string) => {
    try {
      // Stop any currently playing audio
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
      }

      // Create audio from base64 data (MP3 format from OpenAI TTS)
      const audio = new Audio(`data:audio/mpeg;base64,${audioData}`);
      setCurrentAudio(audio);
      setIsSpeaking(true);

      audio.onended = () => {
        setIsSpeaking(false);
        setCurrentAudio(null);
      };

      audio.onerror = () => {
        console.error('Audio playback failed');
        setIsSpeaking(false);
        setCurrentAudio(null);
      };

      await audio.play();
    } catch (error) {
      console.error('TTS playback error:', error);
      setIsSpeaking(false);
      setCurrentAudio(null);
    }
  };

  const stopSpeaking = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
    }
    setIsSpeaking(false);
  };

  // Test voice functionality
  const testVoice = async () => {
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: "Hello, this is a voice test.",
          session_id: sessionIdRef.current || sessionId,
          user_id: userId,
          user_context: {
            ace_score: aceScore,
            ace_details: aceDetails,
            age: userInfo?.age || 25,
            name: userInfo?.name || "User",
            application: variant === "healing-rooms" ? "healing-rooms" : "chatbot",
            avatar_mode: true,
            test_tts: true
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.audio_data) {
        console.log("Testing TTS voice...");
        await speakMessage(data.audio_data);
      } else {
        console.error("Voice test failed:", data.error);
      }
    } catch (error) {
      console.error("Voice test error:", error);
    }
  };

  // Message sending
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      console.log("Sending message to backend...");
      console.log("Session ID:", sessionId);
      console.log("User ID:", userId);
      
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionIdRef.current || sessionId,
          user_id: userId,
          user_context: {
            ace_score: aceScore,
            ace_details: aceDetails,
            age: userInfo?.age || 25,
            name: userInfo?.name || "User",
            application: variant === "healing-rooms" ? "healing-rooms" : "chatbot",
            avatar_mode: avatarMode
          }
        }),
      });

      if (!response.ok) {
        if (response.status === 403) {
          // Handle ACE score restriction
          const errorData = await response.json();
          const restrictionMessage: Message = {
            id: (Date.now() + 1).toString(),
            content: errorData.detail || "Chat access is restricted for your safety. Please contact info@thinkround.org to learn more about our Trauma Transformation Training program.",
            sender: "zoe",
            timestamp: new Date(),
            expression: "caring"
          };
          setMessages(prev => [...prev, restrictionMessage]);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Backend response:", data);

      // Handle ACE score restriction in legacy response format
      if (data.restricted) {
        const restrictionMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response || "Chat access is restricted for your safety. Please contact info@thinkround.org to learn more about our Trauma Transformation Training program.",
          sender: "zoe",
          timestamp: new Date(),
          expression: "caring"
        };
        setMessages(prev => [...prev, restrictionMessage]);
        return;
      }

      // Handle response - display it even if success is false (fallback responses)
      if (data.response) {
        // Capture session ID from response for conversation continuity
        if (data.session_id) {
          if (!sessionId) {
            setSessionId(data.session_id);
            sessionIdRef.current = data.session_id;
            console.log("Session started:", data.session_id);
          } else {
            sessionIdRef.current = data.session_id;
            console.log("Continuing session:", data.session_id);
          }
        } else {
          console.log("No session_id in response:", data);
        }
        
        const expression = analyzeExpression(data.response);
        
        const zoeMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          sender: "zoe",
          timestamp: new Date(),
          expression: expression
        };

        setMessages(prev => [...prev, zoeMessage]);
        
        // Log conversation stats if available
        if (data.conversation_stats) {
          console.log("Conversation stats:", data.conversation_stats);
        }
        
        // Log warning if success is false (fallback or error response)
        if (!data.success) {
          console.warn("Backend returned success=false but provided response:", data.error || "Unknown error");
        }
        
        // Play audio if avatar mode is enabled and audio data is provided
        if (avatarMode && data.audio_data) {
          setTimeout(() => speakMessage(data.audio_data), 800);
        }
      } else if (!data.success) {
        // No response and success is false - throw error
        throw new Error(data.error || "No response from AI");
      } else {
        // No response but success is true - unexpected case
        throw new Error("Received success response but no message content");
      }
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: "I'm having trouble connecting right now. Please try again in a moment.",
        sender: "zoe",
        timestamp: new Date(),
        expression: "concerned"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Render different steps
  if (showSteps) {
    if (step === "ageRestriction") {
      return (
        <div className={`max-w-2xl mx-auto p-6 ${className}`}>
          <AgeRestriction />
        </div>
      );
    }

    if (step === "disclaimer") {
      return (
        <div className={`max-w-4xl mx-auto p-6 ${className}`}>
          <Disclaimer onAccept={handleDisclaimerAccept} />
        </div>
      );
    }

    if (step === "userInfo") {
      return (
        <div className={`max-w-2xl mx-auto p-6 ${className}`}>
          <UserInfoForm 
            onSubmit={handleUserInfoSubmit} 
            onAgeRestriction={() => setStep("ageRestriction")}
            profile={keycloakUserInfo ? {
              id: "",
              name: keycloakUserInfo.name || null,
              firstName: keycloakUserInfo.firstName || null,
              lastName: keycloakUserInfo.lastName || null,
              dateOfBirth: null,
            } : null}
          />
        </div>
      );
    }

    if (step === "questionnaire") {
      return (
        <div className={`max-w-4xl mx-auto p-6 ${className}`}>
          <AceQuestionnaire 
            onComplete={handleQuestionnaireComplete}
            userName={userInfo?.name || "User"}
          />
        </div>
      );
    }

    if (step === "results") {
      return (
        <div className={`max-w-4xl mx-auto p-6 ${className}`}>
          <AceResults 
            score={aceScore} 
            userName={userInfo?.name || "User"}
            onStartChat={handleStartChat}
          />
        </div>
      );
    }
  }

  // Chat interface
  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-pink-50 to-purple-50">
      <div className="container mx-auto px-6 pt-12 pb-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-rose-500 via-pink-500 to-purple-600 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-white/20 backdrop-blur-sm rounded-xl">
                    <Heart className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-white">Chat with Zoe</h1>
                    <p className="text-white/90 text-sm">
                      Your personalized healing companion • {userInfo?.name ? `Chatting with ${userInfo.name}` : "Chatting with you"}
                    </p>
                  </div>
                </div>

                {/* Controls */}
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-white/80 hover:text-white hover:bg-white/10 p-2"
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                  
                  {/* Avatar Mode Toggle */}
                  <div className="flex items-center space-x-2">
                    <User className="w-3 h-3 text-white/80" />
                    <span className="text-white/80 text-xs">Avatar Mode:</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={avatarMode}
                        onChange={(e) => setAvatarMode(e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-white/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-white/30"></div>
                    </label>
                  </div>
                  
                  {/* Test Voice Button */}
                  {avatarMode && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={testVoice}
                      disabled={isSpeaking}
                      className="text-white/80 hover:text-white hover:bg-white/10 p-2"
                      title="Test Voice"
                    >
                      <Play className="w-4 h-4" />
                    </Button>
                  )}
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-white/80 hover:text-white hover:bg-white/10 p-2"
                    title="Reset Conversation"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-white/80 hover:text-white hover:bg-white/10 p-2"
                    title="Show Messages"
                  >
                    <MessageSquare className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              
              {avatarMode && (
                <div className="mt-4 p-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
                  <div className="flex items-center space-x-2">
                    <Volume2 className="w-4 h-4 text-white" />
                    <span className="text-sm font-medium text-white">Voice Mode Active</span>
                  </div>
                  <p className="text-sm text-white/80">
                    AI-Generated Voice
                  </p>
                </div>
              )}
            </div>

            {/* Messages */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-50">
              {avatarMode ? (
                // Avatar Mode - Full Screen Avatar Experience
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <h2 className="text-3xl font-bold text-purple-600 mb-4">Zoe</h2>
                    <div className="flex items-center justify-center space-x-2 mb-6">
                      <div className={`w-3 h-3 rounded-full transition-colors ${
                        isSpeaking ? 'bg-green-500 animate-pulse' : 'bg-yellow-500 animate-pulse'
                      }`}></div>
                      <span className="text-gray-600 font-medium">
                        {isSpeaking ? "Speaking..." : "Thinking"}
                      </span>
                    </div>
                    
                    {/* Full Screen Avatar Character */}
                    <div className="relative w-48 h-60 mx-auto mb-6">
                      {/* Main Body/Container with gentle floating animation */}
                      <div 
                        className={`w-48 h-60 bg-gradient-to-b from-pink-200 to-pink-300 rounded-3xl relative shadow-2xl border-4 border-pink-300 transition-all duration-1000`}
                        style={{ 
                          animation: isSpeaking 
                            ? 'gentle-pulse 2s ease-in-out infinite' 
                            : 'gentle-think 3s ease-in-out infinite'
                        }}
                      >
                        
                        {/* Hair with subtle movement */}
                        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                          {/* Hair buns/sides with gentle sway */}
                          <div className="flex justify-between w-40">
                            <div className={`w-12 h-12 bg-gradient-to-b from-orange-400 to-orange-600 rounded-full transition-transform duration-2000 ${
                              isSpeaking ? 'animate-pulse' : ''
                            }`} style={{ 
                              animation: 'hair-sway-left 4s ease-in-out infinite'
                            }}></div>
                            <div className={`w-12 h-12 bg-gradient-to-b from-orange-400 to-orange-600 rounded-full transition-transform duration-2000 ${
                              isSpeaking ? 'animate-pulse' : ''
                            }`} style={{ 
                              animation: 'hair-sway-right 4s ease-in-out infinite'
                            }}></div>
                          </div>
                          {/* Main hair */}
                          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-28 h-8 bg-gradient-to-b from-orange-500 to-orange-700 rounded-t-full"></div>
                        </div>
                        
                        {/* Face */}
                        <div className="absolute top-6 left-1/2 transform -translate-x-1/2 w-32 h-36 bg-pink-100 rounded-2xl">
                          {/* Left Eye - Realistic with iris and pupil */}
                          <div className="absolute top-12 left-5 w-7 h-4">
                            {/* Eye white (sclera) */}
                            <div className="w-full h-full bg-white rounded-full shadow-inner border border-pink-200"></div>
                            {/* Iris */}
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-gradient-to-b from-blue-400 to-blue-600 rounded-full">
                              {/* Pupil */}
                              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-black rounded-full"></div>
                              {/* Light reflection */}
                              <div className="absolute top-1 left-1 w-1 h-1 bg-white rounded-full opacity-80"></div>
                            </div>
                            {/* Eyelid for blinking */}
                            <div 
                              className="absolute top-0 left-0 w-full bg-pink-100 transition-all duration-150"
                              style={{
                                height: isSpeaking ? '20%' : '60%',
                                animation: 'realistic-blink 4s ease-in-out infinite'
                              }}
                            ></div>
                          </div>

                          {/* Right Eye - Realistic with iris and pupil */}
                          <div className="absolute top-12 right-5 w-7 h-4">
                            {/* Eye white (sclera) */}
                            <div className="w-full h-full bg-white rounded-full shadow-inner border border-pink-200"></div>
                            {/* Iris */}
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-gradient-to-b from-blue-400 to-blue-600 rounded-full">
                              {/* Pupil */}
                              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-black rounded-full"></div>
                              {/* Light reflection */}
                              <div className="absolute top-1 left-1 w-1 h-1 bg-white rounded-full opacity-80"></div>
                            </div>
                            {/* Eyelid for blinking */}
                            <div 
                              className="absolute top-0 left-0 w-full bg-pink-100 transition-all duration-150"
                              style={{
                                height: isSpeaking ? '20%' : '60%',
                                animation: 'realistic-blink 4s ease-in-out infinite'
                              }}
                            ></div>
                          </div>

                          {/* Eyebrows - Natural shape that moves with expressions */}
                          <div className={`absolute top-10 left-5 w-6 h-1 bg-gradient-to-r from-orange-600 to-orange-700 rounded-full transform transition-all duration-300 ${
                            isSpeaking ? 'rotate-6 -translate-y-2' : '-rotate-1'
                          }`}></div>
                          <div className={`absolute top-10 right-5 w-6 h-1 bg-gradient-to-l from-orange-600 to-orange-700 rounded-full transform transition-all duration-300 ${
                            isSpeaking ? '-rotate-6 -translate-y-2' : 'rotate-1'
                          }`}></div>
                          
                          {/* Cheeks - More prominent and realistic */}
                          <div className={`absolute top-16 left-1 w-6 h-5 bg-pink-300 rounded-full opacity-50 blur-sm transition-all duration-500 ${
                            isSpeaking ? 'opacity-70 scale-110' : 'opacity-50'
                          }`}></div>
                          <div className={`absolute top-16 right-1 w-6 h-5 bg-pink-300 rounded-full opacity-50 blur-sm transition-all duration-500 ${
                            isSpeaking ? 'opacity-70 scale-110' : 'opacity-50'
                          }`}></div>
                          
                          {/* Subtle cheek blush - more prominent for joy */}
                          <div className={`absolute top-18 left-2 w-5 h-4 bg-pink-400 rounded-full opacity-40 blur-sm transition-all duration-500 ${
                            isSpeaking ? 'opacity-60 scale-110' : 'opacity-40'
                          }`}></div>
                          <div className={`absolute top-18 right-2 w-5 h-4 bg-pink-400 rounded-full opacity-40 blur-sm transition-all duration-500 ${
                            isSpeaking ? 'opacity-60 scale-110' : 'opacity-40'
                          }`}></div>
                          
                          {/* Nose - More realistic with nostrils */}
                          <div className="absolute top-20 left-1/2 transform -translate-x-1/2">
                            <div className="w-2 h-3 bg-gradient-to-b from-pink-200 to-pink-300 rounded-full"></div>
                            {/* Nostrils */}
                            <div className="absolute bottom-0 left-0 w-1 h-1 bg-pink-400 rounded-full opacity-30"></div>
                            <div className="absolute bottom-0 right-0 w-1 h-1 bg-pink-400 rounded-full opacity-30"></div>
                          </div>
                          
                          {/* Mouth - Different shapes for different states */}
                          <div className="absolute top-24 left-1/2 transform -translate-x-1/2 w-full flex justify-center">
                            {isSpeaking ? (
                              // Speaking mouth - rounded rectangle with border
                              <div 
                                className="w-8 h-5 border-2 border-pink-500 bg-transparent rounded-lg"
                                style={{
                                  animation: 'gentle-speak 0.4s ease-in-out infinite alternate'
                                }}
                              />
                            ) : (
                              // Thinking mouth - slight horizontal line
                              <div className="w-6 h-2 bg-gradient-to-r from-pink-400 via-red-400 to-pink-400 rounded-full shadow-inner opacity-80"></div>
                            )}
                          </div>
                          
                          {/* Subtle facial contours */}
                          <div className="absolute top-14 left-1 w-1 h-8 bg-gradient-to-b from-transparent via-pink-200 to-transparent rounded-full opacity-30"></div>
                          <div className="absolute top-14 right-1 w-1 h-8 bg-gradient-to-b from-transparent via-pink-200 to-transparent rounded-full opacity-30"></div>
                        </div>
                        
                        {/* Body/Shirt with breathing animation */}
                        <div className={`absolute bottom-0 left-1/2 transform -translate-x-1/2 w-20 h-12 bg-gradient-to-b from-pink-400 to-pink-500 rounded-b-2xl transition-all duration-1000 ${
                          isSpeaking ? 'scale-105' : ''
                        }`} style={{
                          animation: 'gentle-breathe 4s ease-in-out infinite'
                        }}></div>
                      </div>
                    </div>
                    
                    {/* Custom CSS animations */}
                    <style jsx>{`
                      @keyframes gentle-float {
                        0%, 100% { transform: translateY(0px) rotate(0deg); }
                        50% { transform: translateY(-8px) rotate(1deg); }
                      }
                      
                      @keyframes gentle-pulse {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                      }
                      
                      @keyframes hair-sway-left {
                        0%, 100% { transform: rotate(-2deg); }
                        50% { transform: rotate(1deg); }
                      }
                      
                      @keyframes hair-sway-right {
                        0%, 100% { transform: rotate(2deg); }
                        50% { transform: rotate(-1deg); }
                      }
                      
                      @keyframes gentle-think {
                        0%, 100% { transform: translateY(0px) rotate(-0.5deg); }
                        33% { transform: translateY(-4px) rotate(0.5deg); }
                        66% { transform: translateY(-2px) rotate(0deg); }
                      }
                      
                      @keyframes realistic-blink {
                        0%, 85%, 100% { height: 30%; }
                        90%, 95% { height: 100%; }
                      }
                      
                      @keyframes gentle-speak {
                        0% { transform: scale(1); }
                        100% { transform: scale(1.1, 0.9); }
                      }
                      
                      @keyframes gentle-breathe {
                        0%, 100% { transform: translateX(-50%) scaleY(1); }
                        50% { transform: translateX(-50%) scaleY(1.1); }
                      }
                    `}</style>

                    <p className="text-gray-500 text-sm">
                      Chatting with Zoe...
                    </p>
                  </div>
                </div>
              ) : (
                // Regular Chat Mode
                <>
                  {messages.length === 0 && (
                    <div className="flex justify-start">
                      <div className="flex items-center space-x-3 max-w-[80%]">
                        <div className="w-10 h-10 bg-gradient-to-r from-rose-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                          <Heart className="w-5 h-5 text-white" />
                        </div>
                        <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border">
                          <p className="text-gray-800">
                            Hello {userInfo?.name || "there"}. I'm here for you — what's on your mind today?
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date().toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`flex items-start space-x-3 max-w-[80%] ${
                          message.sender === "user" ? "flex-row-reverse space-x-reverse" : ""
                        }`}
                      >
                        {/* Avatar */}
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                            message.sender === "user"
                              ? "bg-gradient-to-r from-purple-500 to-indigo-500"
                              : "bg-gradient-to-r from-rose-500 to-pink-500"
                          }`}
                        >
                          {message.sender === "user" ? (
                            <User className="w-5 h-5 text-white" />
                          ) : (
                            <Heart className="w-5 h-5 text-white" />
                          )}
                        </div>

                        {/* Message bubble */}
                        <div
                          className={`rounded-2xl px-4 py-3 ${
                            message.sender === "user"
                              ? "bg-gradient-to-r from-purple-500 to-indigo-500 text-white"
                              : "bg-white text-gray-900 shadow-sm border"
                          }`}
                        >
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {message.content}
                          </p>
                          <p
                            className={`text-xs mt-1 ${
                              message.sender === "user" ? "text-purple-100" : "text-gray-500"
                            }`}
                          >
                            {message.timestamp.toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              )}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-3 max-w-[80%]">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-rose-500 to-pink-500 flex items-center justify-center">
                      <Heart className="w-5 h-5 text-white" />
                    </div>
                    <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-rose-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-rose-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                        <div className="w-2 h-2 bg-rose-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-white border-t border-gray-200 p-4">
              <div className="flex space-x-3">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder={avatarMode ? "Type your message... Zoe will speak her response" : "Share what's on your mind... I'm here to listen."}
                  disabled={isLoading}
                  className="flex-grow text-base py-3 px-4 border-2 border-gray-200 rounded-2xl focus:border-rose-400 focus:ring-rose-400"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-gradient-to-r from-rose-500 to-purple-600 hover:from-rose-600 hover:to-purple-700 text-white rounded-2xl px-5 py-3 shadow-lg transition-all duration-200"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>

              {/* Helper text */}
              <p className="text-xs text-gray-500 mt-2 text-center">
                Zoe is an AI companion designed to provide supportive conversations. For crisis situations, please contact emergency services or a mental health professional.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
