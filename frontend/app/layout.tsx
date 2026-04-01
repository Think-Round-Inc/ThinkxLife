import type React from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import AuthSessionProvider from "@/components/providers/session-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ThinkLife",
  description: "",
  icons: {
    icon: "/tr_logo.png", // main favicon
    shortcut: "/tr_logo.png", // <link rel="shortcut icon">
    apple: "/tr_logo.png", // for iOS homescreen
  },
  generator: "v0.dev",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      {/* Favicon handled via metadata.icons */}
      <body
        className={`${inter.className} bg-white text-gray-800 min-h-screen flex flex-col`}
      >
        <AuthSessionProvider>
          <Navbar />
          <main className="flex-grow pt-10">{children}</main>
          <Footer />
        </AuthSessionProvider>
      </body>
    </html>
  );
}
