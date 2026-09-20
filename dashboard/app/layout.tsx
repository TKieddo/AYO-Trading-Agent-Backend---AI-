import type { Metadata } from "next";
// Use system UI font stack to avoid external font fetches
import "./globals.css";
import { ConditionalLayout } from "@/components/layout/ConditionalLayout";

const systemFontClass = "font-sans";

export const metadata: Metadata = {
  title: "VaultVerse - AI Trading Platform",
  description: "AI Trading Agent Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={systemFontClass} suppressHydrationWarning> 
        <ConditionalLayout>{children}</ConditionalLayout>
      </body>
    </html>
  );
}

