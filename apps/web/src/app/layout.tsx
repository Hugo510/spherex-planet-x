import type { ReactNode } from "react";

// El layout real vive en [locale]/layout.tsx; este solo pasa los hijos.
export default function RootLayout({ children }: { children: ReactNode }) {
  return children;
}
