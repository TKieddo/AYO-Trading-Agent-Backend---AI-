import { NextRequest, NextResponse } from "next/server";
import { getServerSupabase } from "@/lib/supabase/server";

type OptimizationRecord = {
  id: string;
  strategy_id: string;
  status: string;
  [key: string]: any;
};

type OptimizationIterationRecord = {
  parameters: any;
  llm_reasoning: string | null;
  [key: string]: any;
};

/**
 * GET /api/trading/optimize/[id]
 * Get optimization status
 */
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const supabase = getServerSupabase();
    if (!supabase) {
      return NextResponse.json(
        { error: "Database connection unavailable" },
        { status: 500 }
      );
    }

    const { data: optimizationData, error } = await supabase
      .from("strategy_optimizations")
      .select("*")
      .eq("id", id)
      .single();

    if (error || !optimizationData) {
      return NextResponse.json(
        { error: "Optimization not found" },
        { status: 404 }
      );
    }

    const optimization = optimizationData as OptimizationRecord;

    // Get latest iteration for current parameters
    const { data: latestIterationData } = await supabase
      .from("optimization_iterations")
      .select("parameters, llm_reasoning")
      .eq("optimization_id", id)
      .order("iteration_number", { ascending: false })
      .limit(1)
      .single();

    const latestIteration = latestIterationData as OptimizationIterationRecord | null;

    const responseData: any = {
      ...(optimization as any),
      current_parameters: latestIteration?.parameters,
      llm_reasoning: latestIteration?.llm_reasoning,
    };

    return NextResponse.json({
      success: true,
      optimization: responseData,
    });
  } catch (error: any) {
    console.error("Error fetching optimization:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch optimization" },
      { status: 500 }
    );
  }
}

