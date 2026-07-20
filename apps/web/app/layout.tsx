import type { Metadata } from "next";
import { Geist, Geist_Mono, Fraunces } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });
const mono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" });
const wordmark = Fraunces({ subsets: ["latin"], weight: "variable", variable: "--font-wordmark", axes: ["SOFT", "opsz"] });

export const metadata: Metadata = {
  title: "Anagrama — Knowledge, connected",
  description: "An AI-native operating system for understanding.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" className={`${geist.variable} ${mono.variable} ${wordmark.variable}`}><body>{children}</body></html>;
}
