import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, user_context, session_id, user_id } = body;

    // Forward the request to the backend with full session context
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        user_context,
        session_id,
        user_id,
      }),
    });

    if (!response.ok) {
      console.error("Backend response error:", response.status, response.statusText);
      return NextResponse.json(
        { 
          success: false, 
          error: "Backend service unavailable. Please try again later." 
        },
        { status: 503 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { 
        success: false, 
        error: "Unable to process your message. Please try again." 
      },
      { status: 500 }
    );
  }
} 