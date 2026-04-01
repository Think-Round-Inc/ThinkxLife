'use client'

import type React from "react";
import { usePathname } from "next/navigation";

export default function ExteriorSpacesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isPrototype = pathname?.includes('/prototype');

  // Apply immersive layout only for the prototype route
  if (isPrototype) {
    return (
      <div className="fixed inset-0 bg-black text-white overflow-hidden z-50">
        {children}
      </div>
    );
  }

  // Normal layout for the main exterior spaces page
  return <>{children}</>;
} 