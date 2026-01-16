"use client";

import { useState } from "react";
import { MarketPairCard } from "../molecules/MarketPairCard";
import { TradesPositionsTable } from "./TradesPositionsTable";

interface MarketPair {
  pair: string[];
  changePercent: string;
  value: string;
  sliderValue: number;
  price: string;
  totalProfit?: number;
  winCount?: number;
  totalTrades?: number;
  category?: "crypto" | "forex";
}

interface AggregatedPosition {
  symbol: string;
  totalRealizedProfit: number;
  totalUnrealizedPnl: number;
  totalSize: number;
  userCount: number;
  avgEntryPrice: number;
  currentPrice: number;
  longCount: number;
  shortCount: number;
  totalLeverage: number;
}

interface ExploreMarketsSectionProps {
  markets: MarketPair[];
  aggregatedPositions?: AggregatedPosition[];
}

export function ExploreMarketsSection({ 
  markets,
  aggregatedPositions
}: ExploreMarketsSectionProps) {
  const [activeTab, setActiveTab] = useState<"crypto" | "forex">("crypto");

  // Filter markets by category
  const filteredMarkets = markets.filter(market => {
    if (activeTab === "crypto") {
      // Crypto pairs
      return market.category === "crypto" || !market.category;
    } else {
      // Forex pairs
      return market.category === "forex";
    }
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-6">
      {/* Aggregated Positions Table - Left Side (Wide) */}
      <div className="lg:col-span-7 order-2 lg:order-1">
        <TradesPositionsTable
          aggregatedPositions={aggregatedPositions}
        />
      </div>

      {/* Markets Section - Right Side */}
      <div className="lg:col-span-5 order-1 lg:order-2">
        <div className="rounded-2xl border border-black/10 p-4 md:p-6 h-full">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-slate-900 text-base md:text-lg font-semibold">Top Performing Pairs</h2>
            </div>
            
            {/* Tabs */}
            <div className="flex items-center gap-1 bg-slate-100 rounded-md p-0.5 border border-slate-200 mb-2 w-fit">
              <button
                onClick={() => setActiveTab("crypto")}
                className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-all ${
                  activeTab === "crypto"
                    ? "bg-black text-white"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Crypto
              </button>
              <button
                onClick={() => setActiveTab("forex")}
                className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-all ${
                  activeTab === "forex"
                    ? "bg-black text-white"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Forex
              </button>
            </div>
            
            <p className="text-[10px] text-slate-500">Best performing pairs by total profit from closed trades</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
            {filteredMarkets.length > 0 ? (
              filteredMarkets.map((market, index) => (
                <MarketPairCard
                  key={index}
                  pair={market.pair}
                  changePercent={market.changePercent}
                  value={market.value}
                  sliderValue={market.sliderValue}
                  price={market.price}
                  totalProfit={market.totalProfit}
                  winCount={market.winCount}
                  totalTrades={market.totalTrades}
                />
              ))
            ) : (
              <div className="col-span-2 text-center py-8">
                <p className="text-xs text-slate-400">No {activeTab} pairs available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
