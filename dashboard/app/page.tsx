"use client";

import Link from "next/link";
import { useState } from "react";

export default function HomePage() {
  const [selectedTab, setSelectedTab] = useState<"Investors" | "Trading">("Investors");

  return (
    <div className="min-h-screen bg-black text-white flex">
      {/* Left Sidebar Navigation */}
      <aside className="w-20 bg-black border-r border-gray-800 flex flex-col items-center py-6">
        {/* Logo at top */}
        <div className="mb-8">
          <div className="w-10 h-10 grid grid-cols-2 gap-1">
            <div className="w-4 h-4 bg-white rounded-sm"></div>
            <div className="w-4 h-4 bg-white rounded-sm"></div>
            <div className="w-4 h-4 bg-white rounded-sm"></div>
            <div className="w-4 h-4 bg-white rounded-sm"></div>
          </div>
        </div>

        {/* Navigation icons */}
        <nav className="flex-1 flex flex-col gap-4">
          {/* Active icon (Home) */}
          <Link href="/" className="w-12 h-12 bg-yellow-400 rounded-lg flex items-center justify-center">
            <div className="w-6 h-6 grid grid-cols-2 gap-0.5">
              <div className="w-2.5 h-2.5 bg-black rounded-sm"></div>
              <div className="w-2.5 h-2.5 bg-black rounded-sm"></div>
              <div className="w-2.5 h-2.5 bg-black rounded-sm"></div>
              <div className="w-2.5 h-2.5 bg-black rounded-sm"></div>
            </div>
          </Link>

          {/* Dashboard icon */}
          <Link href="/dashboard" className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-colors">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </Link>

          <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>

          <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
            </svg>
          </div>

          <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
        </nav>

        {/* Bottom section */}
        <div className="mt-auto flex flex-col gap-4">
          <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
            </svg>
          </div>

          {/* Profile image */}
          <div className="w-12 h-12 rounded-full border-2 border-yellow-400 overflow-hidden">
            <div className="w-full h-full bg-gray-700 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Navigation Bar */}
        <header className="h-16 bg-black border-b border-gray-800 flex items-center justify-between px-6">
          {/* Left Section */}
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 bg-yellow-400 rotate-45"></div>
            <span className="text-white font-medium">WETH/USDC</span>
            <Link href="/portfolio" className="px-4 py-1.5 border border-white rounded-full text-white text-sm flex items-center gap-2 hover:bg-gray-900 transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
              Portfolio
            </Link>
            <Link href="/charts" className="px-4 py-1.5 border border-white rounded-full text-white text-sm flex items-center gap-2 hover:bg-gray-900 transition-colors">
              <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              Trade
            </Link>
            <div className="w-1 h-1 bg-white rounded-full"></div>
            <div className="w-1 h-1 bg-white rounded-full"></div>
            <div className="w-1 h-1 bg-white rounded-full"></div>
            <span className="text-white text-sm">VaultVerse v.1.0</span>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="searching..."
              className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-yellow-400 w-32"
            />
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <div className="w-10 h-10 bg-yellow-400 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <span className="text-white text-sm">Hello Maurice</span>
            <div className="w-10 h-10 rounded-full border-2 border-yellow-400 overflow-hidden">
              <div className="w-full h-full bg-gray-700 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Grid */}
        <main className="flex-1 p-6 grid grid-cols-12 gap-6 overflow-auto">
          {/* Left Column - Performance & Explore Markets */}
          <div className="col-span-7 flex flex-col gap-6">
            {/* Performance Section */}
            <div className="relative rounded-2xl bg-gray-900 p-6 overflow-hidden">
              {/* Glowing sphere background */}
              <div className="absolute -right-32 -top-32 w-96 h-96 bg-gradient-to-br from-yellow-400/20 via-orange-500/30 to-yellow-500/20 rounded-full blur-3xl opacity-60"></div>
              <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-gradient-to-br from-yellow-400/20 via-orange-500/30 to-yellow-500/20 rounded-full blur-2xl opacity-40"></div>
              
              <div className="relative z-10">
                <div className="flex items-center gap-2 mb-4">
                  <h2 className="text-white text-lg font-semibold">Performance</h2>
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                
                <div className="mb-6">
                  <div className="text-5xl font-bold text-white mb-2">
                    12,7898<span className="text-2xl">.00 $</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-gray-800 rounded-full text-sm text-gray-300">Past Week</span>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-green-400 text-sm">0.004567%</span>
                    </div>
                  </div>
                </div>

                {/* Metric Cards */}
                <div className="grid grid-cols-3 gap-4">
                  {/* Balance */}
                  <div className="bg-gray-800 rounded-xl p-4">
                    <div className="w-10 h-10 bg-yellow-400 rounded-full flex items-center justify-center mb-3">
                      <span className="text-black font-bold text-lg">$</span>
                    </div>
                    <div className="text-white font-semibold text-lg mb-1">$ 15.000</div>
                    <div className="text-gray-400 text-xs">Ballance</div>
                  </div>

                  {/* Leverage */}
                  <div className="bg-gray-800 rounded-xl p-4">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center mb-3">
                      <span className="text-black font-bold">A</span>
                    </div>
                    <div className="text-white font-semibold text-lg mb-1">$ 7.300</div>
                    <div className="text-gray-400 text-xs">Leverage</div>
                  </div>

                  {/* Margin Usage */}
                  <div className="bg-gray-800 rounded-xl p-4">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center mb-3">
                      <svg className="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="text-white font-semibold text-lg mb-1">$ 211.200</div>
                    <div className="text-gray-400 text-xs mb-2">Margin Usage</div>
                    <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-white w-3/4"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Explore Markets Section */}
            <div className="rounded-2xl bg-gray-900 p-6">
              <h2 className="text-white text-lg font-semibold mb-4">Explore markets</h2>
              <div className="grid grid-cols-2 gap-4">
                {/* Market Card 1 */}
                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">Origin</span>
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">SNX</span>
                    </div>
                    <span className="text-green-400 text-xs">0.0067%</span>
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 bg-gray-700 rounded flex items-center justify-center">
                      <span className="text-white text-xs font-bold">X</span>
                    </div>
                    <span className="text-white font-semibold">USD 00,160.10</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-yellow-400 w-1/3"></div>
                    </div>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span className="text-white text-xs">$ 1.02</span>
                  </div>
                </div>

                {/* Market Card 2 */}
                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">Tether</span>
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">XRP</span>
                    </div>
                    <span className="text-green-400 text-xs">0.4567%</span>
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 bg-gray-700 rounded flex items-center justify-center">
                      <span className="text-white text-xs font-bold">X</span>
                    </div>
                    <span className="text-white font-semibold">USD 13,160.10</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-yellow-400 w-2/3"></div>
                    </div>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span className="text-white text-xs">$ 2.50</span>
                  </div>
                </div>

                {/* Market Card 3 */}
                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">Tether</span>
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">XRP</span>
                    </div>
                    <span className="text-green-400 text-xs">0.4567%</span>
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 bg-gray-700 rounded flex items-center justify-center">
                      <span className="text-white text-xs font-bold">X</span>
                    </div>
                    <span className="text-white font-semibold">USD 52,160.10</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-yellow-400 w-4/5"></div>
                    </div>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span className="text-white text-xs">$ 3.75</span>
                  </div>
                </div>

                {/* Market Card 4 */}
                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">Ethereum</span>
                      <span className="px-2 py-1 bg-gray-700 rounded-full text-xs text-white">ETH</span>
                    </div>
                    <span className="text-green-400 text-xs">0.4567%</span>
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 bg-gray-700 rounded flex items-center justify-center">
                      <span className="text-white text-xs font-bold">X</span>
                    </div>
                    <span className="text-white font-semibold">USD 00,001.10</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-yellow-400 w-1/5"></div>
                    </div>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span className="text-white text-xs">$ 0.50</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="col-span-5 flex flex-col gap-6">
            {/* NFT Card */}
            <div className="rounded-2xl bg-gray-900 p-6">
              <div className="w-full h-48 bg-gray-800 rounded-xl mb-4 flex items-center justify-center overflow-hidden">
                <div className="w-32 h-32 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full flex items-center justify-center">
                  <svg className="w-20 h-20 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <div className="flex gap-2">
                <span className="px-3 py-1 bg-gray-800 rounded-full text-xs text-white flex items-center gap-1">
                  Nft
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </span>
                <span className="px-3 py-1 bg-gray-800 rounded-full text-xs text-white flex items-center gap-1">
                  Portfolio
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </span>
              </div>
            </div>

            {/* Circular Progress Chart */}
            <div className="rounded-2xl bg-gray-900 p-6 flex flex-col items-center">
              <div className="relative w-32 h-32 mb-4">
                <svg className="transform -rotate-90 w-32 h-32">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    className="text-gray-700"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 56 * 0.6} ${2 * Math.PI * 56}`}
                    className="text-yellow-400"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-white text-2xl font-bold">60%</span>
                </div>
              </div>
              <span className="text-white text-sm">WETH/USDC</span>
            </div>

            {/* Activity Section */}
            <div className="rounded-2xl bg-gray-900 p-6">
              <h2 className="text-white text-lg font-semibold mb-4">Activity valiue over time</h2>
              
              {/* Toggle Buttons */}
              <div className="flex gap-2 mb-6 bg-gray-800 rounded-lg p-1">
                <button
                  onClick={() => setSelectedTab("Investors")}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedTab === "Investors"
                      ? "bg-gray-700 text-white"
                      : "text-white"
                  }`}
                >
                  Investors
                </button>
                <button
                  onClick={() => setSelectedTab("Trading")}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedTab === "Trading"
                      ? "bg-gray-700 text-white"
                      : "text-white"
                  }`}
                >
                  Trading
                </button>
              </div>

              {/* Bar Chart */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-xs">At a Galence</span>
                  <span className="text-white text-xs">$ 8.900</span>
                </div>
                <div className="flex items-end justify-between gap-1 h-32">
                  {[0.1, 0.2, 0.3, 0.4, 0.5].map((value, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div
                        className={`w-full rounded-t ${
                          index % 2 === 0 ? "bg-yellow-400" : "bg-gray-700"
                        }`}
                        style={{ height: `${Math.random() * 60 + 40}%` }}
                      ></div>
                      <span className="text-gray-400 text-xs mt-2">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Activity Notifications */}
            <div className="rounded-2xl bg-gray-900 p-6 space-y-4">
              {/* Video Call Card */}
              <div className="bg-yellow-400 rounded-xl p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <span className="text-gray-600 text-xs">02 FEB</span>
                </div>
                <div className="w-12 h-12 bg-gray-300 rounded-full mb-3 flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-black font-medium">Video Cal to Jessica Jesper</p>
              </div>

              {/* Payment Reminder Card */}
              <div className="bg-yellow-400 rounded-xl p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                    </div>
                    <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <span className="text-gray-600 text-xs">05 FEB</span>
                </div>
                <div className="w-12 h-12 bg-orange-200 rounded-full mb-3 flex items-center justify-center">
                  <svg className="w-8 h-8 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-black font-medium mb-2">Send payment reminder</p>
                <p className="text-black text-3xl font-bold">$5,789</p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm">
                  Details
                </button>
                <button className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm">
                  Docs
                </button>
                <button className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm">
                  Notes
                </button>
              </div>

              {/* Arrow Icon */}
              <div className="flex justify-end">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
