import { NextRequest, NextResponse } from "next/server";
import { getServerSupabase } from "@/lib/supabase/server";
import { getBinanceEnv, getBinanceUserTrades } from "@/lib/binance";
import { getAsterEnv, getAsterUserTrades } from "@/lib/aster";

// Backfill user trades using Binance or Aster API and rebuild performance
// Env required: BINANCE_API_KEY + BINANCE_API_SECRET OR ASTER_USER_ADDRESS + ASTER_SIGNER_ADDRESS + ASTER_PRIVATE_KEY

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const limit: number = body.limit || 1000; // Binance max 1000, Aster can handle more
    const exchange: string = body.exchange || "binance"; // "binance" or "aster"
    const symbol: string = body.symbol || ""; // Optional symbol filter
    
    const sb = getServerSupabase();
    if (!sb) return NextResponse.json({ error: "Supabase service role missing" }, { status: 500 });

    let fills: any[] = [];
    
    // Fetch trades from selected exchange
    if (exchange === "aster") {
      const env = getAsterEnv();
      if (!env) return NextResponse.json({ error: "Aster API creds missing. Set ASTER_USER_ADDRESS, ASTER_SIGNER_ADDRESS, ASTER_PRIVATE_KEY" }, { status: 400 });
      
      fills = await getAsterUserTrades(env, {
        symbol: symbol || undefined,
        limit,
      });
    } else {
      // Default to Binance
      const env = getBinanceEnv();
      if (!env) return NextResponse.json({ error: "Binance API creds missing. Set BINANCE_API_KEY and BINANCE_API_SECRET" }, { status: 400 });
      
      fills = await getBinanceUserTrades(env, {
        symbol: symbol || undefined,
        limit,
      });
    }
    
    if (!Array.isArray(fills) || fills.length === 0) {
      return NextResponse.json({ error: "No fills found or invalid response" }, { status: 400 });
    }
    
    // Map exchange fills to our schema (works for both Binance and Aster)
    const ordersToSave: any[] = [];
    const tradesToSave: any[] = [];
    
    for (const fill of fills) {
      // Handle both Binance and Aster formats
      // Binance: symbol (e.g., "BTCUSDT"), Aster: symbol (e.g., "BTCUSDT")
      const coin = fill.symbol?.replace("USDT", "") || fill.coin || fill.asset || "UNKNOWN";
      // Binance: isBuyer (true/false), Aster: side ("BUY"/"SELL")
      const isBuy = fill.isBuyer === true || fill.isBuyer === 1 || fill.side === "BUY" || fill.side === "Buy" || fill.side === "B";
      const side = isBuy ? "buy" : "sell";
      const price = Number(fill.price || fill.px || 0);
      const size = Number(fill.qty || fill.size || fill.sz || 0);
      // Binance: realizedPnl, Aster: realizedPnl (may be in different format)
      const realizedPnl = fill.realizedPnl != null ? Number(fill.realizedPnl) : (fill.closedPnl != null ? Number(fill.closedPnl) : null);
      
      // Get timestamp - Binance uses time (ms), Aster uses time (ms)
      let executedAt: string;
      if (fill.time) {
        const timeMs = Number(fill.time);
        executedAt = new Date(timeMs > 1e12 ? timeMs : timeMs * 1000).toISOString();
      } else if (fill.timestamp) {
        const timeMs = Number(fill.timestamp);
        executedAt = new Date(timeMs > 1e12 ? timeMs : timeMs * 1000).toISOString();
      } else {
        executedAt = new Date().toISOString();
      }
      
      // Binance: id (number), Aster: id (number or string)
      const orderId = String(fill.id || fill.orderId || fill.oid || `fill_${coin}_${executedAt}`);
      
      // Save to orders table
      ordersToSave.push({
        order_id: orderId,
        symbol: coin,
        side,
        type: "market",
        size: Math.abs(size),
        price: price > 0 ? price : null,
        status: "filled",
        filled_size: Math.abs(size),
        created_at: executedAt,
        updated_at: executedAt,
      });
      
      // Save to trades table (will link to orders after orders are saved)
      tradesToSave.push({
        symbol: coin,
        side,
        size: Math.abs(size),
        price,
        fee: fill.fee != null ? Number(fill.fee) : 0,
        // Store PnL: null if not realized, otherwise the actual value (can be 0)
        pnl: realizedPnl !== null ? realizedPnl : null,
        executed_at: executedAt,
        order_id_text: orderId, // Store text order_id temporarily for lookup
      });
    }
    
    // Step 1: Save orders first
    if (ordersToSave.length > 0) {
      await sb.from("orders").upsert(ordersToSave as any, { onConflict: "order_id" });
      console.log(`Saved ${ordersToSave.length} orders from ${exchange} fills`);
    }
    
    // Step 2: Resolve order_id strings to UUIDs and save trades
    if (tradesToSave.length > 0) {
      // Build map of order_id (text) -> orders.id (UUID)
      const orderIdMap = new Map<string, string>();
      const orderIdStrings = tradesToSave
        .map(t => (t as any).order_id_text)
        .filter((id): id is string => id != null);
      
      if (orderIdStrings.length > 0) {
        const { data: ordersData } = await sb
          .from("orders")
          .select("id, order_id")
          .in("order_id", orderIdStrings);
        
        if (ordersData && Array.isArray(ordersData)) {
          for (const order of ordersData as any[]) {
            if (order?.order_id && order?.id) {
              orderIdMap.set(String(order.order_id), order.id);
            }
          }
        }
      }
      
      // Map trades with resolved order UUIDs
      const tradesWithOrderUuids = tradesToSave.map((trade: any) => {
        const resolvedOrderId = trade.order_id_text && orderIdMap.has(String(trade.order_id_text))
          ? orderIdMap.get(String(trade.order_id_text))!
          : null;
        
        return {
          symbol: trade.symbol,
          side: trade.side,
          size: trade.size,
          price: trade.price,
          fee: trade.fee,
          pnl: trade.pnl,
          executed_at: trade.executed_at,
          order_id: resolvedOrderId, // Now UUID or null
        };
      });
      
      // Insert trades, handling duplicates gracefully
      for (const trade of tradesWithOrderUuids) {
        try {
          const { error } = await sb.from("trades").insert(trade as any);
          if (error) {
            // Ignore duplicate errors
            console.log(`Skipped duplicate trade: ${error.message}`);
          }
        } catch (err) {
          // Ignore any errors (duplicates, etc.)
        }
      }
      console.log(`Saved ${tradesWithOrderUuids.length} trades from ${exchange} fills`);
    }

    // Rebuild performance_series from trades
    const { data: tdata, error } = await sb
      .from("trades")
      .select("executed_at, pnl")
      .order("executed_at", { ascending: true });
    if (!error && Array.isArray(tdata)) {
      let cumulative = 0;
      const series = tdata.map((t: any) => {
        const daily = t.pnl != null ? Number(t.pnl) : 0;
        cumulative += daily;
        return { date: t.executed_at, value: 10000 + cumulative, pnl: daily };
      });
      if (series.length) {
        const mapped = series.map((s) => ({ date: s.date, value: s.value, pnl: s.pnl }));
        await sb.from("performance_series").upsert(mapped as any, { onConflict: "date" });
      }
    }

    return NextResponse.json({ ok: true });
  } catch (e: any) {
    return NextResponse.json({ error: e.message || "failed" }, { status: 500 });
  }
}


