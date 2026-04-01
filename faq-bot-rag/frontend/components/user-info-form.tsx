"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Brain, Sparkles, User, Calendar } from "lucide-react";

type UserInfo = {
  name: string;
  age: number | null;
};

interface UserProfile {
  id: string;
  name: string | null;
  firstName: string | null;
  lastName: string | null;
  dateOfBirth: string | null;
  [key: string]: any;
}

type UserInfoFormProps = {
  onSubmit: (data: UserInfo) => void;
  onAgeRestriction: () => void;
  profile?: UserProfile | null;
};

export default function UserInfoForm({
  onSubmit,
  onAgeRestriction,
  profile,
}: UserInfoFormProps) {
  const [name, setName] = useState("");
  const [age, setAge] = useState<string>("");
  const [errors, setErrors] = useState<{ name?: string; age?: string }>({});
  const [needsAge, setNeedsAge] = useState(true);

  useEffect(() => {
    if (profile) {
      // Pre-fill name from profile
      const profileName = profile.firstName || profile.name || "";
      setName(profileName);

      // Check if we have age from date of birth
      if (profile.dateOfBirth) {
        const calculatedAge = calculateAge(profile.dateOfBirth);
        if (calculatedAge !== null) {
          setAge(calculatedAge.toString());
          setNeedsAge(false);
        }
      }
    }
  }, [profile]);

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate inputs
    const newErrors: { name?: string; age?: string } = {};

    if (!name.trim()) {
      newErrors.name = "Name is required";
    }

    if (needsAge) {
      if (!age.trim()) {
        newErrors.age = "Age is required";
      } else if (isNaN(Number(age)) || Number(age) <= 0 || Number(age) > 120) {
        newErrors.age = "Please enter a valid age";
      } else if (Number(age) < 18) {
        // Age restriction check
        onAgeRestriction();
        return;
      }
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Clear errors and submit
    setErrors({});
    onSubmit({ name, age: needsAge ? Number(age) : null });
  };

  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-blue-200/50">
      {/* Header */}
      <div className="flex flex-col items-center text-center mb-8">
        <div className="relative mb-6">
          <div className="p-4 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full shadow-lg">
            <Brain className="h-12 w-12 text-white" />
          </div>
          <Sparkles className="w-6 h-6 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
        </div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-700 bg-clip-text text-transparent mb-3">
          Let's Get Started
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl">
          Hi, I'm Zoe, your AI companion. I'm here to provide a safe space for you to share and receive support.
          {needsAge ? " I need to confirm a few details before we begin." : " Let's proceed to help you better."}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="name" className="text-slate-700 font-medium flex items-center gap-2">
            <User className="w-4 h-4" />
            Your Name
          </Label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name"
            className="border-purple-200 focus:border-purple-400 focus:ring-purple-400 rounded-xl py-3 px-4 text-lg"
            disabled={!needsAge && Boolean(profile?.firstName)} // Disable if we have name from profile and don't need age
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
              {errors.name}
            </p>
          )}
        </div>

        {needsAge && (
          <div className="space-y-2">
            <Label htmlFor="age" className="text-slate-700 font-medium flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Your Age
            </Label>
            <Input
              id="age"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter your age"
              className="border-purple-200 focus:border-purple-400 focus:ring-purple-400 rounded-xl py-3 px-4 text-lg"
            />
            {errors.age && (
              <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                {errors.age}
              </p>
            )}
            <p className="text-sm text-slate-500">
              You must be 18 or older to use Zoe
            </p>
          </div>
        )}

        <Button
          type="submit"
          className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white py-3 px-6 rounded-xl font-medium shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105 text-lg"
        >
          Proceed to Questionnaire
        </Button>
      </form>

      {/* Info Card */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Brain className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-800 mb-2">What's Next?</h3>
            <p className="text-blue-700">
              After this, you'll complete a brief questionnaire that helps me understand your experiences better,
              so I can provide more personalized and empathetic support.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
