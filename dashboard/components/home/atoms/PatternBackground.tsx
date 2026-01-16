export function PatternBackground() {
  // Core symbols for the matrix-style pattern
  const symbols = ['X', 'O', '+', '/', '\\', ':', '□', '.'];
  
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <svg 
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 1000 1400"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Large L-shaped block - right side (prominent) */}
        <rect x="750" y="100" width="200" height="400" fill="#84cc16" opacity="0.40" />
        <rect x="750" y="100" width="400" height="80" fill="#84cc16" opacity="0.40" />
        
        {/* Large rectangular blocks */}
        <rect x="800" y="550" width="180" height="120" fill="#84cc16" opacity="0.35" />
        <rect x="850" y="750" width="150" height="100" fill="#84cc16" opacity="0.38" />
        <rect x="50" y="1100" width="200" height="150" fill="#84cc16" opacity="0.36" />
        <rect x="200" y="1250" width="120" height="100" fill="#84cc16" opacity="0.34" />
        
        {/* Horizontal rectangular blocks */}
        <rect x="100" y="800" width="250" height="60" fill="#84cc16" opacity="0.37" />
        <rect x="600" y="950" width="180" height="50" fill="#84cc16" opacity="0.35" />
        
        {/* Dense symbol grid - creating matrix effect */}
        {/* Top section - dense cluster */}
        {Array.from({ length: 25 }).map((_, i) => {
          const x = 50 + (i % 5) * 80;
          const y = 50 + Math.floor(i / 5) * 60;
          const symbol = symbols[i % symbols.length];
          return (
            <text 
              key={`top-${i}`} 
              x={x} 
              y={y} 
              fontSize="10" 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight={i % 3 === 0 ? "bold" : "normal"}
              opacity={0.5 + (i % 3) * 0.1}
            >
              {symbol}
            </text>
          );
        })}
        
        {/* Middle-left dense cluster */}
        {Array.from({ length: 30 }).map((_, i) => {
          const x = 80 + (i % 6) * 70;
          const y = 400 + Math.floor(i / 6) * 50;
          const symbol = symbols[(i * 3) % symbols.length];
          return (
            <text 
              key={`mid-left-${i}`} 
              x={x} 
              y={y} 
              fontSize="9" 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight={i % 4 === 0 ? "bold" : "normal"}
              opacity={0.45 + (i % 4) * 0.08}
            >
              {symbol}
            </text>
          );
        })}
        
        {/* Center area - mixed density */}
        {Array.from({ length: 40 }).map((_, i) => {
          const x = 300 + (i % 8) * 60;
          const y = 500 + Math.floor(i / 8) * 55;
          const symbol = symbols[(i * 5) % symbols.length];
          return (
            <text 
              key={`center-${i}`} 
              x={x} 
              y={y} 
              fontSize={8 + (i % 3)} 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight={i % 5 === 0 ? "bold" : "normal"}
              opacity={0.4 + (i % 5) * 0.06}
            >
              {symbol}
            </text>
          );
        })}
        
        {/* Right side scattered symbols */}
        {Array.from({ length: 20 }).map((_, i) => {
          const x = 600 + (i % 4) * 90;
          const y = 200 + Math.floor(i / 4) * 80;
          const symbol = symbols[(i * 7) % symbols.length];
          return (
            <text 
              key={`right-${i}`} 
              x={x} 
              y={y} 
              fontSize="11" 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight={i % 3 === 0 ? "bold" : "normal"}
              opacity={0.48 + (i % 3) * 0.05}
            >
              {symbol}
            </text>
          );
        })}
        
        {/* Bottom section - dense pattern */}
        {Array.from({ length: 35 }).map((_, i) => {
          const x = 150 + (i % 7) * 75;
          const y = 1000 + Math.floor(i / 7) * 50;
          const symbol = symbols[(i * 2) % symbols.length];
          return (
            <text 
              key={`bottom-${i}`} 
              x={x} 
              y={y} 
              fontSize="10" 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight={i % 4 === 0 ? "bold" : "normal"}
              opacity={0.42 + (i % 4) * 0.07}
            >
              {symbol}
            </text>
          );
        })}
        
        {/* Scattered individual symbols - random placement */}
        {[
          { x: 120, y: 180, symbol: 'X', size: 14, bold: true, opacity: 0.55 },
          { x: 280, y: 250, symbol: 'O', size: 12, bold: false, opacity: 0.50 },
          { x: 450, y: 320, symbol: '+', size: 16, bold: true, opacity: 0.58 },
          { x: 180, y: 450, symbol: '/', size: 11, bold: false, opacity: 0.48 },
          { x: 520, y: 380, symbol: '\\', size: 13, bold: false, opacity: 0.52 },
          { x: 250, y: 550, symbol: ':', size: 10, bold: false, opacity: 0.46 },
          { x: 480, y: 600, symbol: '□', size: 12, bold: true, opacity: 0.54 },
          { x: 150, y: 700, symbol: '.', size: 8, bold: false, opacity: 0.44 },
          { x: 380, y: 750, symbol: 'X', size: 15, bold: true, opacity: 0.56 },
          { x: 550, y: 820, symbol: 'O', size: 13, bold: false, opacity: 0.50 },
          { x: 220, y: 900, symbol: '+', size: 14, bold: true, opacity: 0.54 },
          { x: 420, y: 1050, symbol: '/', size: 11, bold: false, opacity: 0.48 },
          { x: 320, y: 1150, symbol: '\\', size: 12, bold: false, opacity: 0.50 },
          { x: 580, y: 1200, symbol: ':', size: 10, bold: false, opacity: 0.46 },
          { x: 180, y: 1300, symbol: '□', size: 13, bold: true, opacity: 0.52 },
        ].map((item, i) => (
          <text 
            key={`scatter-${i}`}
            x={item.x} 
            y={item.y} 
            fontSize={item.size} 
            fill="#84cc16" 
            fontFamily="monospace" 
            fontWeight={item.bold ? "bold" : "normal"}
            opacity={item.opacity}
          >
            {item.symbol}
          </text>
        ))}
        
        {/* Dense clusters of same symbol - creating texture blocks */}
        {/* X cluster */}
        <g opacity="0.45">
          {Array.from({ length: 12 }).map((_, i) => (
            <text 
              key={`x-cluster-${i}`}
              x={350 + (i % 4) * 15} 
              y={200 + Math.floor(i / 4) * 20} 
              fontSize="9" 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight="bold"
            >
              X
            </text>
          ))}
        </g>
        
        {/* O cluster */}
        <g opacity="0.42">
          {Array.from({ length: 15 }).map((_, i) => (
            <text 
              key={`o-cluster-${i}`}
              x={500 + (i % 5) * 18} 
              y={650 + Math.floor(i / 5) * 22} 
              fontSize="10" 
              fill="#84cc16" 
              fontFamily="monospace"
            >
              O
            </text>
          ))}
        </g>
        
        {/* Slash cluster - creating flow effect */}
        <g opacity="0.40">
          {Array.from({ length: 20 }).map((_, i) => (
            <text 
              key={`slash-cluster-${i}`}
              x={100 + (i % 10) * 12} 
              y={300 + Math.floor(i / 10) * 15} 
              fontSize="8" 
              fill="#84cc16" 
              fontFamily="monospace"
            >
              /
            </text>
          ))}
        </g>
        
        {/* Dot cluster - pixel-like effect */}
        <g opacity="0.38">
          {Array.from({ length: 25 }).map((_, i) => (
            <text 
              key={`dot-cluster-${i}`}
              x={600 + (i % 5) * 20} 
              y={1100 + Math.floor(i / 5) * 18} 
              fontSize="7" 
              fill="#84cc16" 
              fontFamily="monospace"
            >
              .
            </text>
          ))}
        </g>
        
        {/* Branding - AYO and FOREX scattered */}
        <text x="400" y="150" fontSize="22" fill="#84cc16" fontFamily="monospace" fontWeight="bold" opacity="0.65">AYO</text>
        <text x="700" y="300" fontSize="20" fill="#84cc16" fontFamily="monospace" fontWeight="bold" opacity="0.60">FOREX</text>
        <text x="200" y="600" fontSize="24" fill="#84cc16" fontFamily="monospace" fontWeight="bold" opacity="0.62">AYO</text>
        <text x="550" y="850" fontSize="18" fill="#84cc16" fontFamily="monospace" fontWeight="bold" opacity="0.58">FOREX</text>
        <text x="300" y="1050" fontSize="21" fill="#84cc16" fontFamily="monospace" fontWeight="bold" opacity="0.60">AYO</text>
        <text x="650" y="1300" fontSize="19" fill="#84cc16" fontFamily="monospace" fontWeight="bold" opacity="0.58">FOREX</text>
        
        {/* Additional scattered symbols for randomness */}
        {Array.from({ length: 50 }).map((_, i) => {
          const x = (i * 137) % 900 + 50;
          const y = (i * 211) % 1200 + 100;
          const symbol = symbols[(i * 13) % symbols.length];
          const size = 7 + (i % 4);
          return (
            <text 
              key={`random-${i}`}
              x={x} 
              y={y} 
              fontSize={size} 
              fill="#84cc16" 
              fontFamily="monospace" 
              fontWeight={i % 7 === 0 ? "bold" : "normal"}
              opacity={0.35 + (i % 6) * 0.05}
            >
              {symbol}
            </text>
          );
        })}
      </svg>
      
      {/* Subtle glow effects */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-lime-400/20 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-lime-500/18 rounded-full blur-2xl"></div>
    </div>
  );
}
