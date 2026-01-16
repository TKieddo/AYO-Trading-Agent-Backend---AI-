"use client";

import { useState } from "react";

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
  category?: "crypto" | "forex";
}

interface TradesPositionsTableProps {
  aggregatedPositions?: AggregatedPosition[];
}

export function TradesPositionsTable({
  aggregatedPositions = []
}: TradesPositionsTableProps) {
  const [activeTab, setActiveTab] = useState<"crypto" | "forex">("crypto");
  // Format currency
  const formatCurrency = (value: number) => {
    const sign = value >= 0 ? "+" : "";
    return `${sign}$${Math.abs(value).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  // Format number
  const formatNumber = (value: number, decimals: number = 2) => {
    return value.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  };

  // Format percentage
  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? "+" : "";
    return `${sign}${Math.abs(value).toFixed(2)}%`;
  };

  // Filter and sort by total realized profit (descending)
  const filteredPositions = aggregatedPositions.filter(pos => {
    if (activeTab === "crypto") {
      // Crypto pairs typically don't have traditional forex pairs like EUR/USD
      return !pos.symbol.includes("EUR") && !pos.symbol.includes("GBP") && 
             !pos.symbol.includes("JPY") && !pos.symbol.includes("AUD") &&
             !pos.symbol.includes("CAD") && !pos.symbol.includes("CHF") &&
             (pos.category === "crypto" || !pos.category);
    } else {
      // Forex pairs
      return pos.symbol.includes("EUR") || pos.symbol.includes("GBP") || 
             pos.symbol.includes("JPY") || pos.symbol.includes("AUD") ||
             pos.symbol.includes("CAD") || pos.symbol.includes("CHF") ||
             pos.category === "forex";
    }
  });

  const sortedPositions = [...filteredPositions].sort(
    (a, b) => b.totalRealizedProfit - a.totalRealizedProfit
  );

  return (
    <div className="rounded-2xl bg-lime-400/20 border border-lime-400/30 p-3 md:p-4 h-full shadow-sm flex flex-col">
      <div className="mb-4 flex-shrink-0">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-slate-900 text-base font-semibold">Open Positions</h2>
          <span className="text-xs text-slate-500 bg-slate-50 px-2 py-1 rounded-full">
            {sortedPositions.length} pairs
          </span>
        </div>
        
        {/* Tabs */}
        <div className="flex items-center justify-center gap-1 bg-white/50 rounded-md p-0.5 border-2 border-black/30 w-fit mx-auto">
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
        
        <p className="text-[10px] text-slate-500 mt-2">Aggregated positions across all users by trading pair</p>
      </div>
      
      <div className="overflow-hidden rounded-xl border border-lime-400/30 bg-lime-400/20 backdrop-blur-sm flex-1 flex flex-col min-h-0">
        <div className="overflow-y-auto overflow-x-auto" style={{ maxHeight: '350px' }}>
          <table className="w-full min-w-[600px]">
            <thead className="bg-gradient-to-r from-lime-400/30 to-lime-400/20 border-b border-lime-400/40 sticky top-0 z-10">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Pair</th>
                <th className="px-3 py-2 text-right text-xs font-semibold text-slate-700 uppercase tracking-wider">Realized</th>
                <th className="px-3 py-2 text-right text-xs font-semibold text-slate-700 uppercase tracking-wider">Unrealized</th>
                <th className="px-3 py-2 text-right text-xs font-semibold text-slate-700 uppercase tracking-wider">Size</th>
                <th className="px-3 py-2 text-right text-xs font-semibold text-slate-700 uppercase tracking-wider">Price</th>
                <th className="px-3 py-2 text-center text-xs font-semibold text-slate-700 uppercase tracking-wider">Pos</th>
              </tr>
            </thead>
            <tbody className="bg-lime-400/10 divide-y divide-lime-400/20">
              {sortedPositions.length > 0 ? (
                sortedPositions.map((position, index) => {
                  const priceChange = position.currentPrice && position.avgEntryPrice
                    ? ((position.currentPrice - position.avgEntryPrice) / position.avgEntryPrice) * 100
                    : 0;
                  
                  return (
                    <tr 
                      key={position.symbol} 
                      className="hover:bg-gradient-to-r hover:from-lime-400/30 hover:to-lime-400/10 transition-all duration-200 group"
                    >
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-1.5">
                          <div className="w-6 h-6 rounded-md bg-black flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
                            <span className="text-white text-[10px] font-bold">
                              {position.symbol.split('/')[0]?.charAt(0) || '?'}
                            </span>
                          </div>
                          <span className="text-xs font-semibold text-slate-900">{position.symbol}</span>
                        </div>
                      </td>
                      <td className="px-3 py-2 text-right">
                        <span className={`text-xs font-semibold ${
                          position.totalRealizedProfit >= 0 ? "text-green-600" : "text-red-600"
                        }`}>
                          {formatCurrency(position.totalRealizedProfit)}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-right">
                        <span className={`text-xs font-medium ${
                          position.totalUnrealizedPnl >= 0 ? "text-green-600" : "text-red-600"
                        }`}>
                          {formatCurrency(position.totalUnrealizedPnl)}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-right">
                        <span className="text-xs text-slate-700 font-medium">
                          {formatNumber(position.totalSize, 4)}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-right">
                        <div className="flex flex-col items-end gap-0.5">
                          <span className="text-xs font-semibold text-slate-900">
                            ${formatNumber(position.currentPrice, 2)}
                          </span>
                          <span className={`text-[10px] font-medium ${
                            priceChange >= 0 ? "text-green-600" : "text-red-600"
                          }`}>
                            {formatPercentage(priceChange)}
                          </span>
                        </div>
                      </td>
                      <td className="px-3 py-2 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-green-50 text-green-700 border border-green-200">
                            {position.longCount}L
                          </span>
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-50 text-red-700 border border-red-200">
                            {position.shortCount}S
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-3 py-8 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <svg className="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <p className="text-xs text-slate-400 font-medium">No open positions</p>
                      <p className="text-[10px] text-slate-300">Positions will appear here when users start trading</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
