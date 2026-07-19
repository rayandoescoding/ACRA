import type { Metadata } from "next";

import { ibmPlexMono, ibmPlexSans } from "@/lib/fonts";

import "./globals.css";

export const metadata: Metadata = {
  title: "ACRA",
  description: "Autonomous customer resolution operations console.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${ibmPlexSans.variable} ${ibmPlexMono.variable} font-sans`}>
        {children}
      </body>
    </html>
  );
}
