"use client";

import ChatInterface from "@/components/chat-interface";

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <ChatInterface 
        className="h-screen"
        variant="general"
        showSteps={true}
        initialStep="disclaimer"
      />
    </div>
  );
} 