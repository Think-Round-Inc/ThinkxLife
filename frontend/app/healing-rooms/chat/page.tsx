"use client";

import ChatInterface from "@/components/chat-interface";

export default function HealingRoomsChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-pink-50 to-purple-50">
      <ChatInterface 
        className="h-screen"
        variant="healing-rooms"
        showSteps={true}
        initialStep="disclaimer"
      />
    </div>
  );
} 