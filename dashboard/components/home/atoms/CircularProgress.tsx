interface CircularProgressProps {
  value: number; // 0-100
  size?: number;
  label?: string;
  className?: string;
}

export function CircularProgress({ 
  value, 
  size = 128, 
  label,
  className = "" 
}: CircularProgressProps) {
  const radius = size / 2 - 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-slate-200"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className="text-yellow-400 transition-all duration-300"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-slate-900 text-2xl font-bold">{value}%</span>
        </div>
      </div>
      {label && <span className="text-slate-700 text-sm mt-4">{label}</span>}
    </div>
  );
}
