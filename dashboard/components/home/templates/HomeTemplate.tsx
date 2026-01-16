"use client";

import { HomeTopbar } from "../organisms/HomeTopbar";
import { PerformanceSection } from "../organisms/PerformanceSection";
import { ExploreMarketsSection } from "../organisms/ExploreMarketsSection";
import { RightSidebar } from "../organisms/RightSidebar";
import { PatternBackground } from "../atoms/PatternBackground";
import { HeroBottomEdge } from "../atoms/HeroBottomEdge";
import { FeaturesSection } from "../organisms/FeaturesSection";
import { HowItWorksSection } from "../organisms/HowItWorksSection";
import { DevelopmentNoticePopup } from "../organisms/DevelopmentNoticePopup";

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

interface HomeTemplateProps {
  performanceData: {
    total: string;
    period: string;
    change: string;
    strategies?: Array<{
      pair: string;
      profit: string;
      profitPercent: string;
      performance: string;
      category?: "crypto" | "forex";
    }>;
    cryptoStrategies?: Array<{
      pair: string;
      profit: string;
      profitPercent: string;
      performance: string;
    }>;
    forexStrategies?: Array<{
      pair: string;
      profit: string;
      profitPercent: string;
      performance: string;
    }>;
    metrics?: Array<{
      icon: React.ReactNode;
      iconVariant?: "yellow" | "white";
      value: string;
      label: string;
      progress?: number;
    }>;
    rightSidebar?: {
      nftImage?: React.ReactNode;
      progressValue?: number;
      progressLabel?: string;
      activityChartData?: {
        data: number[];
        labels: string[];
        maxValue: string;
        title: string;
      };
      notifications?: Array<{
        icon: React.ReactNode;
        date: string;
        avatar?: React.ReactNode;
        title: string;
        amount?: string;
        variant?: "default" | "payment";
      }>;
    };
  };
  marketsData: Array<{
    pair: string[];
    changePercent: string;
    value: string;
    sliderValue: number;
    price: string;
    totalProfit?: number;
    winCount?: number;
    totalTrades?: number;
  }>;
  aggregatedPositions?: AggregatedPosition[];
}

export function HomeTemplate({
  performanceData,
  marketsData,
  aggregatedPositions
}: HomeTemplateProps) {
  return (
    <div className="min-h-screen bg-[#e8eaec] flex flex-col">
      {/* Development Notice Popup */}
      <DevelopmentNoticePopup />

      {/* Hero Section - Full width, pure black with pattern background */}
      <div className="relative w-full bg-black overflow-hidden">
        {/* Pattern background for entire hero section */}
        <div className="absolute inset-0">
          <PatternBackground />
        </div>
        
        {/* Decorative bottom edge */}
        <HeroBottomEdge />
        
        {/* Topbar - Dark themed */}
        <div className="relative z-20">
          <HomeTopbar />
        </div>
        
        {/* Hero content */}
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6 p-4 md:p-6 pt-6 pb-16 md:pb-24">
          {/* Performance Section - Left Side Only */}
          <div className="md:col-span-8">
            <PerformanceSection data={performanceData} />
          </div>

          {/* Right Sidebar - Separate */}
          {performanceData.rightSidebar && (
            <div className="md:col-span-4">
              <RightSidebar
                nftImage={performanceData.rightSidebar.nftImage}
                progressValue={performanceData.rightSidebar.progressValue}
                progressLabel={performanceData.rightSidebar.progressLabel}
              />
            </div>
          )}
        </div>
      </div>
      
      {/* Spacing between hero and main content */}
      <div className="h-8 md:h-12 bg-[#e8eaec]"></div>
      
      {/* Explore Markets Section - Two Column Layout (separate, white) */}
      <main className="flex-1 p-4 md:p-6">
        <ExploreMarketsSection 
          markets={marketsData}
          aggregatedPositions={aggregatedPositions}
        />
      </main>

      {/* Features Section - Light themed */}
      <FeaturesSection />

      {/* How It Works Section - Dark themed */}
      <HowItWorksSection />
    </div>
  );
}
