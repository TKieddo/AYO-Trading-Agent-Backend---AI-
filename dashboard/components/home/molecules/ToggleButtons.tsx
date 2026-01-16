"use client";

interface ToggleButtonsProps<T extends string> {
  options: T[];
  selected: T;
  onSelect: (value: T) => void;
}

export function ToggleButtons<T extends string>({ 
  options, 
  selected, 
  onSelect 
}: ToggleButtonsProps<T>) {
  return (
    <div className="flex gap-2 bg-slate-100 rounded-lg p-1">
      {options.map((option) => (
        <button
          key={option}
          onClick={() => onSelect(option)}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selected === option
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600"
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
