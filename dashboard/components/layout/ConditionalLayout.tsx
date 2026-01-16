"use client";

import { usePathname } from "next/navigation";
import { Topbar } from "@/components/layout/Topbar";
import { Footer } from "@/components/layout/Footer";

export function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isHomePage = pathname === "/";

  if (isHomePage) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="mx-auto max-w-7xl w-full px-4 sm:px-6 py-4 flex-1 flex flex-col">
        <Topbar />
        <main className="pt-2 space-y-6 flex-1">{children}</main>
        <Footer />
      </div>
    </div>
  );
}
