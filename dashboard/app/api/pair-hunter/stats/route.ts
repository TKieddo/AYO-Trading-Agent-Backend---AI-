import { NextRequest, NextResponse } from "next/server";
import { getServerSupabase } from "@/lib/supabase/server";

/**
 * GET /api/pair-hunter/stats
 * Returns pair hunter performance stats keyed by asset.
 */
export async function GET() {
  try {
    const supabase = getServerSupabase();
    if (!supabase) {
      return NextResponse.json({ stats: {} });
    }

    const { data, error } = await supabase
      .from("pair_hunter_stats")
      .select("*")
      .order("asset", { ascending: true });

    if (error) {
      console.error("Error fetching pair_hunter_stats:", error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const stats: Record<string, any> = {};
    for (const row of data || []) {
      const asset = String(row.asset || "").toUpperCase();
      if (!asset) continue;
      stats[asset] = {
        total_trades: Number(row.total_trades || 0),
        wins: Number(row.wins || 0),
        losses: Number(row.losses || 0),
        win_rate: Number(row.win_rate || 0),
        total_pnl_usd: Number(row.total_pnl_usd || 0),
        total_pnl_percent: Number(row.total_pnl_percent || 0),
        expectancy_usd: Number(row.expectancy_usd || 0),
        expectancy_percent: Number(row.expectancy_percent || 0),
        last_close_reason: row.last_close_reason || "",
        last_updated: row.last_updated || row.updated_at || new Date().toISOString(),
      };
    }

    return NextResponse.json({ stats });
  } catch (error: any) {
    console.error("Error in pair-hunter stats GET:", error);
    return NextResponse.json({ error: error.message || "Failed to fetch stats" }, { status: 500 });
  }
}

/**
 * POST /api/pair-hunter/stats
 * Upserts one pair hunter stat row.
 */
export async function POST(req: NextRequest) {
  try {
    const supabase = getServerSupabase();
    if (!supabase) {
      return NextResponse.json({ error: "Database unavailable" }, { status: 500 });
    }

    const body = await req.json();
    const asset = String(body?.asset || "").toUpperCase().trim();
    const stats = body?.stats || {};
    if (!asset) {
      return NextResponse.json({ error: "asset is required" }, { status: 400 });
    }

    const row = {
      asset,
      total_trades: Number(stats.total_trades || 0),
      wins: Number(stats.wins || 0),
      losses: Number(stats.losses || 0),
      win_rate: Number(stats.win_rate || 0),
      total_pnl_usd: Number(stats.total_pnl_usd || 0),
      total_pnl_percent: Number(stats.total_pnl_percent || 0),
      expectancy_usd: Number(stats.expectancy_usd || 0),
      expectancy_percent: Number(stats.expectancy_percent || 0),
      last_close_reason: String(stats.last_close_reason || ""),
      last_updated: stats.last_updated || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const { error } = await supabase
      .from("pair_hunter_stats")
      .upsert(row as any, { onConflict: "asset" });

    if (error) {
      console.error("Error upserting pair_hunter_stats:", error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error("Error in pair-hunter stats POST:", error);
    return NextResponse.json({ error: error.message || "Failed to upsert stats" }, { status: 500 });
  }
}
