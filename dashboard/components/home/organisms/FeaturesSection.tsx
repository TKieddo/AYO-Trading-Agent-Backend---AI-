"use client";

export function FeaturesSection() {
  return (
    <div className="w-full py-8 md:py-16 px-4 md:px-6 bg-gradient-to-b from-[#e8eaec] via-white to-[#e8eaec] relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-lime-400/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-yellow-400/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-400/5 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header Section */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-2 mb-4">
            <svg className="w-5 h-5 text-lime-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-slate-700 text-sm font-semibold">What you'll get</span>
          </div>
          <h2 className="text-slate-900 text-2xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-4">
            AI-Powered Trading. Real-Time Decisions.
          </h2>
          <p className="text-slate-600 text-base md:text-lg max-w-2xl mx-auto px-4">
            Automate your trading with intelligent AI agents that analyze markets, execute trades, and manage positions 24/7.
          </p>
        </div>

        {/* Top Row - 3 Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
          {/* Card 1: Automated Trading */}
          <div className="bg-white rounded-lg p-6 border border-slate-200/80 shadow-lg hover:shadow-2xl hover:border-slate-300/60 transition-all duration-300 relative overflow-hidden group backdrop-blur-sm">
            {/* Unique trading chart pattern */}
            <div className="absolute top-0 right-0 w-48 h-48 -mr-24 -mt-24 opacity-8 group-hover:opacity-12 transition-opacity">
              <svg className="w-full h-full" viewBox="0 0 192 192">
                <defs>
                  <linearGradient id="tradingGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#000000" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#1a1a1a" stopOpacity="0.3" />
                  </linearGradient>
                </defs>
                {/* Upward trending chart pattern */}
                <path d="M20 150 L40 130 L60 140 L80 110 L100 90 L120 70 L140 50 L160 30 L172 20" 
                      fill="none" stroke="url(#tradingGradient)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                {/* Chart bars */}
                <rect x="30" y="130" width="8" height="20" fill="#000000" opacity="0.6" rx="1"/>
                <rect x="50" y="120" width="8" height="30" fill="#000000" opacity="0.6" rx="1"/>
                <rect x="70" y="110" width="8" height="40" fill="#000000" opacity="0.6" rx="1"/>
                <rect x="90" y="80" width="8" height="70" fill="#000000" opacity="0.6" rx="1"/>
                <rect x="110" y="60" width="8" height="90" fill="#000000" opacity="0.6" rx="1"/>
                {/* Upward arrow */}
                <path d="M150 40 L160 30 L150 20 M160 30 L170 30" 
                      fill="none" stroke="#000000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.8"/>
              </svg>
            </div>
            <div className="relative z-10">
              <div className="bg-gradient-to-br from-lime-50 to-lime-100 rounded-lg p-4 mb-4 border border-lime-200">
                <div className="text-lime-600 text-xs font-semibold mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Portfolio Growth
                </div>
                <div className="h-24 relative">
                  <svg className="w-full h-full" viewBox="0 0 200 70" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="barGradient1" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#84cc16" stopOpacity="1" />
                        <stop offset="100%" stopColor="#65a30d" stopOpacity="1" />
                      </linearGradient>
                      <linearGradient id="barGradient2" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#84cc16" stopOpacity="1" />
                        <stop offset="100%" stopColor="#65a30d" stopOpacity="1" />
                      </linearGradient>
                      <linearGradient id="barGradient3" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#84cc16" stopOpacity="1" />
                        <stop offset="100%" stopColor="#65a30d" stopOpacity="1" />
                      </linearGradient>
                    </defs>
                    {/* Bar 1 - Week 1 */}
                    <rect x="20" y="30" width="35" height="18" fill="url(#barGradient1)" rx="3" />
                    <text x="37.5" y="65" fontSize="9" fill="#64748b" textAnchor="middle" fontWeight="500">Week 1</text>
                    {/* Bar 2 - Week 2 */}
                    <rect x="75" y="20" width="35" height="28" fill="url(#barGradient2)" rx="3" />
                    <text x="92.5" y="65" fontSize="9" fill="#64748b" textAnchor="middle" fontWeight="500">Week 2</text>
                    {/* Bar 3 - Today */}
                    <rect x="130" y="5" width="35" height="43" fill="url(#barGradient3)" rx="3" />
                    <text x="147.5" y="65" fontSize="9" fill="#64748b" textAnchor="middle" fontWeight="500">Today</text>
                  </svg>
                </div>
              </div>
              <h3 className="text-slate-900 text-lg font-bold mb-2">Automated Trading</h3>
              <p className="text-slate-600 text-sm">AI agents execute trades 24/7 based on real-time market analysis and technical indicators.</p>
            </div>
          </div>

          {/* Card 2: Real-Time Decisions */}
          <div className="bg-white rounded-lg p-6 border border-slate-200/80 shadow-lg hover:shadow-2xl hover:border-slate-300/60 transition-all duration-300 relative overflow-hidden group backdrop-blur-sm">
            {/* Unique AI brain/neural network pattern */}
            <div className="absolute top-0 right-0 w-48 h-48 -mr-24 -mt-24 opacity-8 group-hover:opacity-12 transition-opacity">
              <svg className="w-full h-full" viewBox="0 0 192 192">
                <defs>
                  <radialGradient id="neuralGradient" cx="50%" cy="50%">
                    <stop offset="0%" stopColor="#000000" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#000000" stopOpacity="0.2" />
                  </radialGradient>
                </defs>
                {/* Neural network nodes */}
                <circle cx="50" cy="50" r="8" fill="#000000" opacity="0.7"/>
                <circle cx="100" cy="40" r="10" fill="#000000" opacity="0.8"/>
                <circle cx="150" cy="60" r="8" fill="#000000" opacity="0.7"/>
                <circle cx="60" cy="100" r="9" fill="#000000" opacity="0.75"/>
                <circle cx="120" cy="110" r="8" fill="#000000" opacity="0.7"/>
                <circle cx="160" cy="130" r="10" fill="#000000" opacity="0.8"/>
                <circle cx="80" cy="150" r="8" fill="#000000" opacity="0.7"/>
                {/* Neural connections */}
                <line x1="50" y1="50" x2="100" y2="40" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                <line x1="100" y1="40" x2="150" y2="60" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                <line x1="50" y1="50" x2="60" y2="100" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                <line x1="100" y1="40" x2="120" y2="110" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                <line x1="150" y1="60" x2="160" y2="130" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                <line x1="60" y1="100" x2="80" y2="150" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                <line x1="120" y1="110" x2="160" y2="130" stroke="#000000" strokeWidth="1.5" opacity="0.4"/>
                {/* Central decision node */}
                <circle cx="100" cy="100" r="12" fill="url(#neuralGradient)" stroke="#000000" strokeWidth="2" opacity="0.9"/>
              </svg>
            </div>
            <div className="relative z-10">
              <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-3 mb-4 border border-yellow-200">
                <div className="flex items-start gap-2 mb-2">
                  <svg className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded font-medium">ANALYZED</span>
                      <span className="text-[10px] text-green-600 bg-green-100 px-2 py-0.5 rounded font-semibold">NEW</span>
                    </div>
                    <div className="text-slate-900 text-sm font-bold mb-1">Agent Decision: BUY ETH/USDC</div>
                    <div className="text-[10px] text-slate-600 mb-1">RSI: 28 (oversold) • EMA20 above price • Entry: $2,480</div>
                    <div className="text-[10px] text-slate-500">2 seconds ago</div>
                  </div>
                </div>
              </div>
              <h3 className="text-slate-900 text-lg font-bold mb-2">Real-Time Decisions</h3>
              <p className="text-slate-600 text-sm">Get instant AI-powered trading decisions based on RSI, EMA, MACD, and market conditions.</p>
            </div>
          </div>

          {/* Card 3: Performance Tracking */}
          <div className="bg-white rounded-lg p-6 border border-slate-200/80 shadow-lg hover:shadow-2xl hover:border-slate-300/60 transition-all duration-300 relative overflow-hidden group backdrop-blur-sm">
            {/* Unique analytics dashboard pattern */}
            <div className="absolute top-0 right-0 w-48 h-48 -mr-24 -mt-24 opacity-8 group-hover:opacity-12 transition-opacity">
              <svg className="w-full h-full" viewBox="0 0 192 192">
                <defs>
                  <linearGradient id="analyticsGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#000000" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#1a1a1a" stopOpacity="0.4" />
                  </linearGradient>
                </defs>
                {/* Grid pattern */}
                <line x1="20" y1="40" x2="172" y2="40" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="20" y1="80" x2="172" y2="80" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="20" y1="120" x2="172" y2="120" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="20" y1="160" x2="172" y2="160" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="40" y1="20" x2="40" y2="172" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="80" y1="20" x2="80" y2="172" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="120" y1="20" x2="120" y2="172" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                <line x1="160" y1="20" x2="160" y2="172" stroke="#000000" strokeWidth="1" opacity="0.3"/>
                {/* Performance line */}
                <path d="M30 150 L50 130 L70 140 L90 110 L110 90 L130 70 L150 50 L170 40" 
                      fill="none" stroke="url(#analyticsGradient)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                {/* Data points */}
                <circle cx="50" cy="130" r="4" fill="#000000" opacity="0.8"/>
                <circle cx="90" cy="110" r="4" fill="#000000" opacity="0.8"/>
                <circle cx="130" cy="70" r="4" fill="#000000" opacity="0.8"/>
                <circle cx="170" cy="40" r="5" fill="#000000" opacity="0.9"/>
              </svg>
            </div>
            <div className="relative z-10">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 mb-4 border border-blue-200">
                <div className="h-20 relative">
                  <svg className="w-full h-full" viewBox="0 0 200 60" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="profitGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.7" />
                        <stop offset="50%" stopColor="#3b82f6" stopOpacity="0.9" />
                        <stop offset="100%" stopColor="#3b82f6" stopOpacity="1" />
                      </linearGradient>
                      <filter id="profitGlow">
                        <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>
                    {/* Grid lines */}
                    <line x1="0" y1="50" x2="200" y2="50" stroke="#cbd5e1" strokeWidth="0.5" opacity="0.5" />
                    <line x1="0" y1="30" x2="200" y2="30" stroke="#cbd5e1" strokeWidth="0.5" opacity="0.5" />
                    <line x1="0" y1="10" x2="200" y2="10" stroke="#cbd5e1" strokeWidth="0.5" opacity="0.5" />
                    {/* Realistic line graph with ups and downs */}
                    <polyline
                      points="5,45 15,42 25,48 35,38 45,35 55,42 65,30 75,28 85,35 95,25 105,32 115,28 125,35 135,22 145,18 155,25 165,20 175,15 185,12 195,8"
                      fill="none"
                      stroke="url(#profitGradient)"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      filter="url(#profitGlow)"
                    />
                    {/* Area fill under the line */}
                    <polygon
                      points="5,45 15,42 25,48 35,38 45,35 55,42 65,30 75,28 85,35 95,25 105,32 115,28 125,35 135,22 145,18 155,25 165,20 175,15 185,12 195,8 195,60 5,60"
                      fill="url(#profitGradient)"
                      opacity="0.15"
                    />
                    {/* Glowing dot at end */}
                    <circle cx="195" cy="8" r="4" fill="#3b82f6" filter="url(#profitGlow)" opacity="0.9" />
                    <circle cx="195" cy="8" r="2" fill="#ffffff" />
                  </svg>
                </div>
              </div>
              <h3 className="text-slate-900 text-lg font-bold mb-2">Performance Tracking</h3>
              <p className="text-slate-600 text-sm">Monitor your portfolio growth, win rates, and trading performance with detailed analytics.</p>
            </div>
          </div>
        </div>

        {/* Bottom Row - 2 Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8 md:mb-12">
          {/* Card 4: Multi-Asset Support */}
          <div className="rounded-lg p-6 border border-black/20 shadow-lg hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
            {/* Unique multi-asset/trading pairs visualization */}
            <div className="absolute top-0 right-0 w-48 h-48 -mr-24 -mt-24 opacity-8 group-hover:opacity-12 transition-opacity">
              <svg className="w-full h-full" viewBox="0 0 192 192">
                <defs>
                  <linearGradient id="assetGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#000000" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#1a1a1a" stopOpacity="0.4" />
                  </linearGradient>
                </defs>
                {/* Currency symbols pattern */}
                <circle cx="60" cy="50" r="12" fill="#000000" opacity="0.7"/>
                <text x="60" y="55" fontSize="10" fill="#ffffff" textAnchor="middle" fontWeight="bold" opacity="0.9">$</text>
                <circle cx="120" cy="40" r="12" fill="#000000" opacity="0.7"/>
                <text x="120" y="45" fontSize="10" fill="#ffffff" textAnchor="middle" fontWeight="bold" opacity="0.9">€</text>
                <circle cx="160" cy="70" r="12" fill="#000000" opacity="0.7"/>
                <text x="160" y="75" fontSize="10" fill="#ffffff" textAnchor="middle" fontWeight="bold" opacity="0.9">£</text>
                <circle cx="50" cy="110" r="12" fill="#000000" opacity="0.7"/>
                <text x="50" y="115" fontSize="8" fill="#ffffff" textAnchor="middle" fontWeight="bold" opacity="0.9">₿</text>
                <circle cx="110" cy="120" r="12" fill="#000000" opacity="0.7"/>
                <text x="110" y="125" fontSize="8" fill="#ffffff" textAnchor="middle" fontWeight="bold" opacity="0.9">Ξ</text>
                <circle cx="150" cy="140" r="12" fill="#000000" opacity="0.7"/>
                <text x="150" y="145" fontSize="8" fill="#ffffff" textAnchor="middle" fontWeight="bold" opacity="0.9">◎</text>
                {/* Connection lines */}
                <line x1="60" y1="50" x2="120" y2="40" stroke="#000000" strokeWidth="1.5" opacity="0.3"/>
                <line x1="120" y1="40" x2="160" y2="70" stroke="#000000" strokeWidth="1.5" opacity="0.3"/>
                <line x1="60" y1="50" x2="50" y2="110" stroke="#000000" strokeWidth="1.5" opacity="0.3"/>
                <line x1="120" y1="40" x2="110" y2="120" stroke="#000000" strokeWidth="1.5" opacity="0.3"/>
                <line x1="160" y1="70" x2="150" y2="140" stroke="#000000" strokeWidth="1.5" opacity="0.3"/>
                {/* Central hub */}
                <circle cx="100" cy="90" r="16" fill="url(#assetGradient)" stroke="#000000" strokeWidth="2" opacity="0.9"/>
              </svg>
            </div>
            <div className="relative z-10">
              <div className="rounded-lg p-4 mb-4 border border-black/20">
                <div className="mb-3">
                  <div className="text-slate-900 text-xs font-semibold mb-2">Supported Markets</div>
                  <div className="flex items-center gap-1 text-[10px] text-slate-600">
                    <span className="bg-black px-2 py-0.5 rounded text-white font-medium">Crypto</span>
                    <span className="text-slate-400">•</span>
                    <span className="bg-black px-2 py-0.5 rounded text-white font-medium">Forex</span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2.5">
                  {/* Trading Pair Icons with labels */}
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white font-bold text-xs">BTC</span>
                    </div>
                    <span className="text-[9px] text-slate-700 font-medium">Bitcoin</span>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white font-bold text-xs">ETH</span>
                    </div>
                    <span className="text-[9px] text-slate-700 font-medium">Ethereum</span>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white font-bold text-xs">SOL</span>
                    </div>
                    <span className="text-[9px] text-slate-700 font-medium">Solana</span>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white font-bold text-xs">EUR</span>
                    </div>
                    <span className="text-[9px] text-slate-700 font-medium">Euro</span>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white font-bold text-xs">GBP</span>
                    </div>
                    <span className="text-[9px] text-slate-700 font-medium">Pound</span>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-blue-500 rounded-lg flex items-center justify-center shadow-md">
                      <span className="text-white font-bold text-xs">JPY</span>
                    </div>
                    <span className="text-[9px] text-slate-700 font-medium">Yen</span>
                  </div>
                </div>
              </div>
              <h3 className="text-slate-900 text-lg font-bold mb-2">Multi-Asset Support</h3>
              <p className="text-slate-600 text-sm">Trade crypto and forex pairs with unified AI decision-making across all markets.</p>
            </div>
          </div>

          {/* Card 5: Risk Management */}
          <div className="bg-white rounded-lg p-6 border border-black/20 shadow-lg hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
            {/* Unique shield/security pattern */}
            <div className="absolute top-0 right-0 w-48 h-48 -mr-24 -mt-24 opacity-15 group-hover:opacity-20 transition-opacity">
              <svg className="w-full h-full" viewBox="0 0 192 192">
                <defs>
                  <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#000000" stopOpacity="0.95" />
                    <stop offset="100%" stopColor="#1a1a1a" stopOpacity="0.5" />
                  </linearGradient>
                </defs>
                {/* Shield shape */}
                <path d="M96 30 L140 50 L140 90 Q140 130 120 150 Q100 170 96 170 Q92 170 72 150 Q52 130 52 90 L52 50 Z" 
                      fill="url(#shieldGradient)" stroke="#000000" strokeWidth="2" opacity="0.9"/>
                {/* Lock icon */}
                <rect x="82" y="100" width="28" height="24" rx="2" fill="#000000" opacity="0.8"/>
                <path d="M82 100 Q96 90 96 90 Q96 90 110 100" fill="none" stroke="#000000" strokeWidth="2" opacity="0.8"/>
                <circle cx="96" cy="112" r="4" fill="#ffffff" opacity="0.9"/>
                {/* Security lines */}
                <line x1="70" y1="80" x2="122" y2="80" stroke="#000000" strokeWidth="2" opacity="0.6"/>
                <line x1="70" y1="70" x2="122" y2="70" stroke="#000000" strokeWidth="1.5" opacity="0.5"/>
                <line x1="70" y1="90" x2="122" y2="90" stroke="#000000" strokeWidth="1.5" opacity="0.5"/>
              </svg>
            </div>
            <div className="relative z-10">
              <div className="rounded-lg p-4 mb-4 border border-black/20" style={{ backgroundColor: '#36383a' }}>
                <div className="text-white text-xs font-bold mb-3">AI Risk Controls</div>
                <div className="space-y-2.5">
                  {/* ATR-Based Stop Loss */}
                  <div className="flex items-center justify-between bg-black/10 rounded-lg p-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center shadow-sm">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </div>
                      <div>
                        <div className="text-white text-[10px] font-semibold">ATR Stop Loss</div>
                        <div className="text-slate-300 text-[9px]">Dynamic: 2.0x ATR</div>
                      </div>
                    </div>
                    <span className="text-white text-[10px] font-bold">-2.5%</span>
                  </div>
                  {/* Take Profit */}
                  <div className="flex items-center justify-between bg-black/10 rounded-lg p-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center shadow-sm">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <div className="text-white text-[10px] font-semibold">Take Profit</div>
                        <div className="text-slate-300 text-[9px]">1.5x Risk/Reward</div>
                      </div>
                    </div>
                    <span className="text-white text-[10px] font-bold">+3.75%</span>
                  </div>
                  {/* Position Sizing */}
                  <div className="flex items-center justify-between bg-black/10 rounded-lg p-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center shadow-sm">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <div>
                        <div className="text-white text-[10px] font-semibold">Position Size</div>
                        <div className="text-slate-300 text-[9px]">Signal strength based</div>
                      </div>
                    </div>
                    <span className="text-white text-[10px] font-bold">10-15%</span>
                  </div>
                </div>
              </div>
              <h3 className="text-slate-900 text-lg font-bold mb-2">AI Risk Management</h3>
              <p className="text-slate-600 text-sm">ATR-based dynamic stops, trailing stops, and intelligent position sizing based on RSI/EMA/MACD signal strength.</p>
            </div>
          </div>
        </div>

        {/* Bottom Feature List */}
        <div className="flex flex-wrap items-center justify-center gap-3 md:gap-6">
          {[
            "AI Decision Engine",
            "Real-Time Analytics",
            "Position Management",
            "Multi-Exchange Support",
            "24/7 Monitoring",
            "Performance Dashboard",
            "Risk Controls"
          ].map((feature, index) => (
            <div key={index} className="flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <svg className="w-4 h-4 text-lime-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span className="text-slate-700 text-sm font-medium">{feature}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
