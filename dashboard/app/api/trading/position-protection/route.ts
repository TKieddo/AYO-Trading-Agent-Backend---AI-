import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000").replace(/\/$/, "");

/**
 * POST /api/trading/position-protection
 * Updates TP/SL for an existing position by replacing protection orders on exchange.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { asset, symbol, tp_price, sl_price } = body || {};
    const target = asset || symbol;

    if (!target) {
      return NextResponse.json(
        { error: "Missing required field: asset or symbol" },
        { status: 400 }
      );
    }

    // Require at least one side to be provided (can be null/"" to clear one side while setting the other).
    if (tp_price === undefined && sl_price === undefined) {
      return NextResponse.json(
        { error: "Provide at least one of tp_price or sl_price" },
        { status: 400 }
      );
    }

    const response = await fetch(`${PYTHON_API_URL}/api/position-protection`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset: target, tp_price, sl_price }),
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      return NextResponse.json(
        { error: result?.error || `Python API returned ${response.status}` },
        { status: response.status }
      );
    }

    return NextResponse.json(result);
  } catch (error: any) {
    console.error("Position protection update error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to update position protection" },
      { status: 500 }
    );
  }
}

