import { Badge } from "../atoms/Badge";

interface MarketPairCardProps {
  pair: string[];
  changePercent: string;
  value: string;
  sliderValue: number; // 0-100
  price: string;
  totalProfit?: number;
  winCount?: number;
  totalTrades?: number;
}

export function MarketPairCard({ 
  pair, 
  changePercent, 
  value, 
  sliderValue,
  price,
  totalProfit,
  winCount,
  totalTrades
}: MarketPairCardProps) {
  const isPositive = changePercent.startsWith("+") || !changePercent.startsWith("-");
  
  const formatCurrency = (value: number) => {
    const sign = value >= 0 ? "+" : "";
    return `${sign}$${Math.abs(value).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  const winRate = totalTrades && totalTrades > 0 && winCount !== undefined
    ? Math.round((winCount / totalTrades) * 100)
    : null;
  
  return (
    <div className="group relative bg-black border border-slate-700/50 rounded-xl p-3 md:p-4 shadow-sm hover:shadow-md transition-all duration-300 hover:border-slate-600">
      {/* Subtle glow effect on hover */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-yellow-400/0 to-yellow-400/0 group-hover:from-yellow-400/10 group-hover:to-transparent transition-all duration-300 pointer-events-none"></div>
      
      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <div className="flex gap-1.5 items-center">
            {pair.map((token, index) => (
              <Badge key={index} variant="gray">{token}</Badge>
            ))}
          </div>
          <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-md ${
            isPositive 
              ? "text-green-400 bg-green-900/30" 
              : "text-red-400 bg-red-900/30"
          }`}>
            {changePercent}
          </span>
        </div>
        
        {/* Total Profit from Closed Trades */}
        {totalProfit !== undefined && (
          <div className="mb-3">
            <div className="flex items-baseline gap-1">
              <span className="text-[10px] text-slate-400 font-medium">Total Profit:</span>
              <span className={`text-sm font-bold ${
                totalProfit >= 0 ? "text-green-400" : "text-red-400"
              }`}>
                {formatCurrency(totalProfit)}
              </span>
            </div>
          </div>
        )}
        
        {/* Win Rate and Trade Stats */}
        {(winRate !== null || totalTrades !== undefined) && (
          <div className="flex items-center gap-3 text-xs">
            {winRate !== null && (
              <div className="flex items-center gap-1">
                <span className="text-slate-400">Win Rate:</span>
                <span className="font-semibold text-white">{winRate}%</span>
              </div>
            )}
            {totalTrades !== undefined && (
              <div className="flex items-center gap-1">
                <span className="text-slate-400">Trades:</span>
                <span className="font-semibold text-white">{totalTrades}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
