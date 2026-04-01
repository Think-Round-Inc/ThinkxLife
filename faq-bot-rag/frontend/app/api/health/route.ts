import { NextRequest, NextResponse } from "next/server"

// GET /api/health - Health check
export async function GET(request: NextRequest) {
  try {
    return NextResponse.json({
      status: "healthy",
      service: "ThinkLife Frontend",
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Health check failed:", error)
    
    return NextResponse.json({
      status: "unhealthy",
      error: error instanceof Error ? error.message : "Unknown error",
      timestamp: new Date().toISOString(),
    }, { status: 503 })
  }
}
