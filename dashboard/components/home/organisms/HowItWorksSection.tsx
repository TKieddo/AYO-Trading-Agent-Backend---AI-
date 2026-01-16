"use client";

export function HowItWorksSection() {
  return (
    <div className="w-full py-8 md:py-16 px-4 md:px-6 bg-white">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-8 md:mb-12">
          <h2 className="text-black text-2xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-4">How It Works</h2>
          <p className="text-slate-600 text-base md:text-lg px-4">
            Four steps to automated AI-powered trading with real-time market analysis and execution.
          </p>
        </div>

        {/* Four Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {/* Card 1: Market Analysis */}
          <div className="bg-black rounded-xl p-4 md:p-6 shadow-lg">
            <div className="mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">Market Analysis</h3>
            <p className="text-slate-300 text-sm mb-4">
              AI analyzes real-time market data using RSI, EMA, MACD, and ATR indicators every interval.
            </p>
            {/* Technical Indicators Visual */}
            <div className="rounded-lg p-4 mt-4" style={{ backgroundColor: '#36383a' }}>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">RSI (14)</span>
                  <span className="text-lime-400 text-xs font-semibold">28.5</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">EMA (20)</span>
                  <span className="text-blue-400 text-xs font-semibold">$2,480</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">MACD</span>
                  <span className="text-green-400 text-xs font-semibold">+12.5</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">ATR</span>
                  <span className="text-yellow-400 text-xs font-semibold">$62</span>
                </div>
              </div>
            </div>
          </div>

          {/* Card 2: AI Decision Making */}
          <div className="bg-black rounded-xl p-4 md:p-6 shadow-lg">
            <div className="mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">AI Decision Making</h3>
            <p className="text-slate-300 text-sm mb-4">
              Advanced LLM evaluates market conditions and generates structured trading decisions in real-time.
            </p>
            {/* AI Decision Visual */}
            <div className="rounded-lg p-4 mt-4" style={{ backgroundColor: '#36383a' }}>
              <div className="text-slate-400 text-xs mb-2">Latest Decision</div>
              <div className="bg-green-500/20 border border-green-500/30 rounded-lg px-2 py-1.5 mb-2">
                <div className="text-green-400 text-xs font-bold mb-1">BUY ETH/USDC</div>
                <div className="text-slate-300 text-[10px]">RSI oversold • EMA bullish • Entry: $2,480</div>
              </div>
              <div className="text-slate-500 text-[10px]">Decision time: 2.3s</div>
            </div>
          </div>

          {/* Card 3: Risk Management */}
          <div className="bg-black rounded-xl p-4 md:p-6 shadow-lg">
            <div className="mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">Risk Management</h3>
            <p className="text-slate-300 text-sm mb-4">
              Automated ATR-based stop loss, take profit orders, and intelligent position sizing protect your capital.
            </p>
            {/* Risk Controls Visual */}
            <div className="rounded-lg p-4 mt-4" style={{ backgroundColor: '#36383a' }}>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">Stop Loss</span>
                  <span className="text-red-400 text-xs font-semibold">-2.5% (ATR 2.0x)</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">Take Profit</span>
                  <span className="text-green-400 text-xs font-semibold">+3.75% (1.5x R/R)</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 text-xs">Position Size</span>
                  <span className="text-blue-400 text-xs font-semibold">10-15%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Card 4: Automated Execution */}
          <div className="bg-black rounded-xl p-4 md:p-6 shadow-lg">
            <div className="mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-white text-xl font-semibold mb-2">Automated Execution</h3>
            <p className="text-slate-300 text-sm mb-4">
              Market orders execute instantly at optimal prices. TP/SL orders monitor positions 24/7.
            </p>
            {/* Execution Flow Visual */}
            <div className="rounded-lg p-4 mt-4" style={{ backgroundColor: '#36383a' }}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-lime-500 rounded-lg flex items-center justify-center">
                    <span className="text-white text-[10px] font-bold">AI</span>
                  </div>
                  <span className="text-white text-xs">Decision</span>
                </div>
                <div className="flex-1 mx-3 relative">
                  <div className="h-0.5 bg-slate-700"></div>
                  <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-lime-400 rounded-full animate-pulse"></div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                    <span className="text-white text-[10px] font-bold">EX</span>
                  </div>
                  <span className="text-white text-xs">Exchange</span>
                </div>
              </div>
              <div className="text-slate-500 text-[10px] mt-2">Execution: &lt;500ms • Interval: 5m</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
