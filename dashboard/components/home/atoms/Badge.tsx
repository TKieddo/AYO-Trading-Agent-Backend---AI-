interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "gray";
  className?: string;
}

export function Badge({ children, variant = "default", className = "" }: BadgeProps) {
  const baseClasses = "px-2 py-1 rounded-full text-xs";
  const variantClasses = variant === "gray" 
    ? "bg-slate-200 text-slate-700" 
    : "bg-slate-100 text-slate-700";
  
  return (
    <span className={`${baseClasses} ${variantClasses} ${className}`}>
      {children}
    </span>
  );
}
