"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Brain, Sparkles, CheckCircle, XCircle } from "lucide-react";

const ACE_QUESTIONS = [
  "Before 18 years old, Did a parent or other adult in the household often swear at you, insult you, put you down, or humiliate you?",
  "Before 18 years old, Did a parent or other adult in the household often push, grab, slap, or throw something at you?",
  "Before 18 years old, Did an adult or person at least 5 years older ever touch, fondle, or have you touch them in a sexual way?",
  "Before 18 years old, Did you often feel that no one in your family loved you or thought you were important or special?",
  "Before 18 years old, Did you often feel that you didn't have enough to eat, had to wear dirty clothes, or had no one to protect you?",
  "Before 18 years old, Were your parents ever separated, divorced, or did a biological parent leave you for another reason?",
  "Before 18 years old, Was your mother or stepmother often pushed, grabbed, slapped, or had something thrown at her?",
  "Before 18 years old, Did you live with anyone who was a problem drinker, alcoholic, or who used street drugs?",
  "Before 18 years old, Was a household member depressed, mentally ill, or did they ever attempt suicide?",
  "Before 18 years old, Did a household member go to jail or prison?",
];

type Answer = "yes" | "no" | null;

type AceQuestionnaireProps = {
  onComplete: (score: number, answers: Answer[], aceDetails: string[]) => void;
  userName: string;
};

export default function AceQuestionnaire({
  onComplete,
  userName,
}: AceQuestionnaireProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>(
    Array(ACE_QUESTIONS.length).fill(null),
  );
  const [currentAnswer, setCurrentAnswer] = useState<Answer>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleNext = useCallback(() => {
    if (currentAnswer === null) return;

    const newAnswers = [...answers];
    newAnswers[currentQuestion] = currentAnswer;

    setAnswers(newAnswers);

    if (currentQuestion < ACE_QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setCurrentAnswer(null);
    } else {
      // Calculate score and extract ACE details
      const score = calculateAceScore(newAnswers);
      const aceDetails = getAceDetails(newAnswers);
      onComplete(score, newAnswers, aceDetails);
    }
  }, [currentAnswer, answers, currentQuestion, onComplete]);

  // Auto-advance to next question after selection
  useEffect(() => {
    if (currentAnswer !== null && !isTransitioning) {
      setIsTransitioning(true);

      // Small delay for visual feedback
      setTimeout(() => {
        handleNext();
        setIsTransitioning(false);
      }, 800);
    }
  }, [currentAnswer, isTransitioning, handleNext]);

  const calculateAceScore = (answers: Answer[]): number => {
    return answers.reduce((score, answer) => {
      if (answer === "yes") return score + 1;
      return score;
    }, 0);
  };

  const getAceDetails = (answers: Answer[]): string[] => {
    const details: string[] = [];
    answers.forEach((answer, index) => {
      if (answer === "yes") {
        details.push(ACE_QUESTIONS[index]);
      }
    });
    return details;
  };

  const progress = ((currentQuestion + 1) / ACE_QUESTIONS.length) * 100;

  const handleAnswerSelect = (value: string) => {
    setCurrentAnswer(value as Answer);
  };

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
        <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-blue-700 bg-clip-text text-transparent mb-2">
          Hi {userName}, let's complete this questionnaire
        </h1>
        <p className="text-sm text-slate-600 max-w-2xl">
          These questions help me understand your experiences better so I can provide more personalized support.
          Your answers are completely confidential and will only be used to tailor our conversations.
        </p>
      </div>

      {/* Progress */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between text-sm text-slate-600 font-medium">
          <span>
            Question {currentQuestion + 1} of {ACE_QUESTIONS.length}
          </span>
          <span>{Math.round(progress)}% Complete</span>
        </div>
        <Progress
          value={progress}
          className="h-2 bg-slate-200"
        />
      </div>

      {/* Question Card */}
      <Card className="bg-gradient-to-r from-slate-50 to-purple-50 border border-purple-200 shadow-lg mb-6">
        <CardContent className="pt-6 pb-4">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 leading-relaxed">
            {ACE_QUESTIONS[currentQuestion]}
          </h3>

          <RadioGroup
            value={currentAnswer || ""}
            onValueChange={handleAnswerSelect}
            className="space-y-3"
            disabled={isTransitioning}
          >
            <div className={`flex items-center space-x-3 p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer hover:bg-green-50 hover:shadow-md transform hover:scale-[1.02] ${
              currentAnswer === "yes" ? "border-green-500 bg-green-50 shadow-md scale-[1.02]" : "border-slate-200 hover:border-green-300"
            }`}>
              <RadioGroupItem value="yes" id="yes" className="text-green-600" />
              <Label htmlFor="yes" className="flex items-center gap-2 cursor-pointer flex-1 font-medium">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Yes
              </Label>
            </div>

            <div className={`flex items-center space-x-3 p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer hover:bg-blue-50 hover:shadow-md transform hover:scale-[1.02] ${
              currentAnswer === "no" ? "border-blue-500 bg-blue-50 shadow-md scale-[1.02]" : "border-slate-200 hover:border-blue-300"
            }`}>
              <RadioGroupItem value="no" id="no" className="text-blue-600" />
              <Label htmlFor="no" className="flex items-center gap-2 cursor-pointer flex-1 font-medium">
                <XCircle className="w-4 h-4 text-blue-600" />
                No
              </Label>
            </div>
          </RadioGroup>

          {/* Auto-advance indicator */}
          {currentAnswer && (
            <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <p className="text-blue-700 font-medium text-sm">
                  {currentQuestion < ACE_QUESTIONS.length - 1
                    ? "Moving to next question..."
                    : "Completing questionnaire..."
                  }
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Manual Next Button (backup) */}
      {!isTransitioning && (
        <Button
          onClick={handleNext}
          disabled={currentAnswer === null}
          className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white py-2.5 px-6 rounded-xl font-medium shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {currentQuestion < ACE_QUESTIONS.length - 1
            ? "Next Question"
            : "Complete Questionnaire"}
        </Button>
      )}

      {/* Support Message */}
      <div className="mt-6 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <div className="p-1.5 bg-blue-100 rounded-lg">
            <Brain className="h-4 w-4 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-800 mb-1 text-sm">You're doing great, {userName}</h3>
            <p className="text-blue-700 text-sm">
              Remember, there are no right or wrong answers. I'm here to provide support regardless of your responses.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
