import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ichin Search",
  description: "Search engine for the Ichin ecosystem",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-stone-50 text-stone-900">{children}</body>
    </html>
  );
}
