import { HomeTopbar } from "../organisms/HomeTopbar";
import { PerformanceSection } from "../organisms/PerformanceSection";
import { ExploreMarketsSection } from "../organisms/ExploreMarketsSection";

interface HomeTemplateProps {
  performanceData: {
    total: string;
    period: string;
    change: string;
    metrics: Array<{
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
  }>;
}

export function HomeTemplate({
  performanceData,
  marketsData
}: HomeTemplateProps) {
  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      <HomeTopbar />
      
      <main className="flex-1 p-6 grid grid-cols-12 gap-6 overflow-auto">
        {/* Full Width Performance Section with Right Sidebar */}
        <div className="col-span-12">
          <PerformanceSection data={performanceData} />
        </div>

        {/* Explore Markets Section */}
        <div className="col-span-12">
          <ExploreMarketsSection markets={marketsData} />
        </div>
      </main>
    </div>
  );
}
