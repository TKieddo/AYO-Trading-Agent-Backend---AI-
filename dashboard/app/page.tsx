"use client";

import { HomeTemplate } from "@/components/home/templates/HomeTemplate";

// Seeded random number generator for deterministic data
function seededRandom(seed: number) {
  let value = seed;
  return () => {
    value = (value * 9301 + 49297) % 233280;
    return value / 233280;
  };
}

export default function HomePage() {
  // Generate 30 days of profit/loss data for Crypto
  const generateCryptoProfitLossData = () => {
    const data: number[] = [];
    const labels: string[] = [];
    const random = seededRandom(12345); // Fixed seed for crypto
    
    for (let i = 0; i < 30; i++) {
      // Generate realistic profit/loss values (can be positive or negative)
      // Simulate market volatility with some trends
      const baseValue = (random() - 0.4) * 30000; // Can be negative
      const trend = i * 200; // Slight upward trend over time
      const volatility = (random() - 0.5) * 8000;
      const profitLoss = baseValue + trend + volatility;
      
      data.push(profitLoss);
      // Sequential day labels: 1, 2, 3, ..., 30
      labels.push((i + 1).toString());
    }
    
    const highValue = Math.max(...data);
    const lowValue = Math.min(...data);
    const totalProfit = data.reduce((sum, val) => sum + val, 0);
    
    return { data, labels, highValue, lowValue, totalProfit };
  };

  // Generate 30 days of profit/loss data for Forex
  const generateForexProfitLossData = () => {
    const data: number[] = [];
    const labels: string[] = [];
    const random = seededRandom(67890); // Fixed seed for forex
    
    for (let i = 0; i < 30; i++) {
      // Forex typically has smaller profit/loss values but more consistent
      const baseValue = (random() - 0.3) * 20000; // Can be negative
      const trend = i * 100; // Gentle upward trend
      const volatility = (random() - 0.5) * 4000;
      const profitLoss = baseValue + trend + volatility;
      
      data.push(profitLoss);
      // Sequential day labels: 1, 2, 3, ..., 30
      labels.push((i + 1).toString());
    }
    
    const highValue = Math.max(...data);
    const lowValue = Math.min(...data);
    const totalProfit = data.reduce((sum, val) => sum + val, 0);
    
    return { data, labels, highValue, lowValue, totalProfit };
  };

  const cryptoProfitLossData = generateCryptoProfitLossData();
  const forexProfitLossData = generateForexProfitLossData();

  // Right sidebar data
  const rightSidebarData = {
    progressValue: 60,
    progressLabel: "WETH/USDC",
    cryptoProfitLossData: cryptoProfitLossData,
    forexProfitLossData: forexProfitLossData,
    notifications: [
      {
        icon: (
          <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        ),
        date: "02 FEB",
        avatar: (
          <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
        ),
        title: "Video Cal to Jessica Jesper",
        variant: "default" as const
      },
      {
        icon: (
          <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        ),
        date: "05 FEB",
        avatar: (
          <div className="w-12 h-12 bg-orange-200 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
        ),
        title: "Send payment reminder",
        amount: "$5,789",
        variant: "payment" as const
      }
    ]
  };

  // Performance data
  const performanceData = {
    total: "12,7898.00",
    period: "Past Week",
    change: "0.004567%",
    cryptoStrategies: [
      {
        pair: "ETH/USDC",
        profit: "+$2,450.00",
        profitPercent: "+12.5%",
        performance: "High Performance"
      },
      {
        pair: "BTC/USD",
        profit: "+$5,890.00",
        profitPercent: "+18.3%",
        performance: "Excellent"
      },
      {
        pair: "SOL/USD",
        profit: "+$1,230.00",
        profitPercent: "+8.7%",
        performance: "Great Performance"
      }
    ],
    forexStrategies: [
      {
        pair: "EUR/USD",
        profit: "+$3,200.00",
        profitPercent: "+15.2%",
        performance: "Excellent"
      },
      {
        pair: "GBP/USD",
        profit: "+$1,850.00",
        profitPercent: "+9.8%",
        performance: "High Performance"
      },
      {
        pair: "USD/JPY",
        profit: "+$950.00",
        profitPercent: "+6.4%",
        performance: "Good Performance"
      }
    ],
    rightSidebar: rightSidebarData
  };

  // Top performing pairs based on closed trades (sorted by total profit)
  const marketsData = [
    {
      pair: ["ETH", "USDC"],
      changePercent: "+2.45%",
      value: "USD 2,480.50",
      sliderValue: 85,
      price: "$ 2,480.50",
      totalProfit: 45230.75,
      winCount: 142,
      totalTrades: 198,
      category: "crypto" as const
    },
    {
      pair: ["BTC", "USD"],
      changePercent: "+1.89%",
      value: "USD 43,200.00",
      sliderValue: 78,
      price: "$ 43,200.00",
      totalProfit: 38920.50,
      winCount: 118,
      totalTrades: 165,
      category: "crypto" as const
    },
    {
      pair: ["SOL", "USD"],
      changePercent: "-0.25%",
      value: "USD 95.50",
      sliderValue: 65,
      price: "$ 95.50",
      totalProfit: 18250.30,
      winCount: 89,
      totalTrades: 132,
      category: "crypto" as const
    },
    {
      pair: ["AVAX", "USD"],
      changePercent: "+1.32%",
      value: "USD 37.50",
      sliderValue: 55,
      price: "$ 37.50",
      totalProfit: 15230.60,
      winCount: 76,
      totalTrades: 98,
      category: "crypto" as const
    },
    {
      pair: ["EUR", "USD"],
      changePercent: "+0.85%",
      value: "USD 1.0850",
      sliderValue: 72,
      price: "$ 1.0850",
      totalProfit: 12450.80,
      winCount: 95,
      totalTrades: 145,
      category: "forex" as const
    },
    {
      pair: ["GBP", "USD"],
      changePercent: "+0.62%",
      value: "USD 1.2650",
      sliderValue: 68,
      price: "$ 1.2650",
      totalProfit: 9850.40,
      winCount: 78,
      totalTrades: 112,
      category: "forex" as const
    }
  ];

  // Sample aggregated positions data (grouped by trading pair)
  const aggregatedPositions = [
    {
      symbol: "ETH/USDC",
      totalRealizedProfit: 45230.75,
      totalUnrealizedPnl: 12850.25,
      totalSize: 125.5,
      userCount: 47,
      avgEntryPrice: 2400.00,
      currentPrice: 2480.50,
      longCount: 32,
      shortCount: 15,
      totalLeverage: 8.5,
      category: "crypto" as const
    },
    {
      symbol: "BTC/USD",
      totalRealizedProfit: 38920.50,
      totalUnrealizedPnl: 15230.00,
      totalSize: 8.75,
      userCount: 38,
      avgEntryPrice: 42000.00,
      currentPrice: 43200.00,
      longCount: 28,
      shortCount: 10,
      totalLeverage: 6.2,
      category: "crypto" as const
    },
    {
      symbol: "SOL/USD",
      totalRealizedProfit: 18250.30,
      totalUnrealizedPnl: 5420.75,
      totalSize: 450.0,
      userCount: 29,
      avgEntryPrice: 100.00,
      currentPrice: 95.50,
      longCount: 12,
      shortCount: 17,
      totalLeverage: 4.8,
      category: "crypto" as const
    },
    {
      symbol: "XRP/USD",
      totalRealizedProfit: 8950.20,
      totalUnrealizedPnl: -1250.50,
      totalSize: 125000.0,
      userCount: 22,
      avgEntryPrice: 0.52,
      currentPrice: 0.48,
      longCount: 18,
      shortCount: 4,
      totalLeverage: 3.5,
      category: "crypto" as const
    },
    {
      symbol: "AVAX/USD",
      totalRealizedProfit: 15230.60,
      totalUnrealizedPnl: 4250.90,
      totalSize: 850.0,
      userCount: 25,
      avgEntryPrice: 35.20,
      currentPrice: 37.50,
      longCount: 20,
      shortCount: 5,
      totalLeverage: 4.0,
      category: "crypto" as const
    },
    {
      symbol: "EUR/USD",
      totalRealizedProfit: 12450.80,
      totalUnrealizedPnl: 3250.40,
      totalSize: 125000.0,
      userCount: 18,
      avgEntryPrice: 1.0820,
      currentPrice: 1.0850,
      longCount: 15,
      shortCount: 3,
      totalLeverage: 5.2,
      category: "forex" as const
    },
    {
      symbol: "GBP/USD",
      totalRealizedProfit: 9850.40,
      totalUnrealizedPnl: 2150.20,
      totalSize: 85000.0,
      userCount: 15,
      avgEntryPrice: 1.2600,
      currentPrice: 1.2650,
      longCount: 12,
      shortCount: 3,
      totalLeverage: 4.0,
      category: "forex" as const
    }
  ];

  return (
    <HomeTemplate
      performanceData={performanceData}
      marketsData={marketsData}
      aggregatedPositions={aggregatedPositions}
    />
  );
}
