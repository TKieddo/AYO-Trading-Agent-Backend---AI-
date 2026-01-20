import { NextResponse } from "next/server";

const PYTHON_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

export async function GET() {
  try {
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for faster failure
    
    const response = await fetch(`${PYTHON_API_URL}/status`, {
      method: "GET",
      headers: { 
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      },
      cache: "no-store",
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      // 404 means agent isn't running - return gracefully without error
      if (response.status === 404) {
        return NextResponse.json(
          { 
            connected: false,
            status: "offline",
            error: "Python agent is not running",
            timestamp: new Date().toISOString()
          },
          { status: 200 } // Return 200 so frontend can handle it gracefully
        );
      }
      
      const errorText = await response.text().catch(() => "");
      return NextResponse.json(
        { 
          connected: false,
          status: "error",
          error: errorText || `Python API returned ${response.status}`,
          timestamp: new Date().toISOString()
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Return the status data directly, matching Python API format
    return NextResponse.json({
      connected: data.connected !== false,
      status: data.status || (data.connected ? "online" : "offline"),
      network: data.network || data.network_label,
      exchange: data.exchange,
      balance: data.balance,
      account_value: data.account_value,
      positions_count: data.positions_count,
      timestamp: data.timestamp || new Date().toISOString(),
    }, {
      headers: {
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
      },
    });
  } catch (error: any) {
    // Only log unexpected errors - connection errors are expected when agent isn't running
    const isExpectedError = 
      error.name === "AbortError" || 
      error.name === "TimeoutError" ||
      error.code === 'ECONNREFUSED' ||
      error.message?.includes("aborted") ||
      error.message?.includes("fetch failed") ||
      error.message?.includes("ECONNREFUSED");
    
    if (!isExpectedError && process.env.NODE_ENV === 'development') {
      console.error("Status check error:", error);
    }
    
    // Handle timeout or network errors
    if (error.name === "AbortError" || error.name === "TimeoutError" || error.message?.includes("aborted")) {
      return NextResponse.json(
        { 
          connected: false,
          status: "timeout",
          error: "Connection timeout - Python agent may be offline",
          timestamp: new Date().toISOString()
        },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { 
        connected: false,
        status: "error",
        error: error.message || "Failed to connect to Python agent",
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

// Also support POST for compatibility
export async function POST() {
  return GET();
}
