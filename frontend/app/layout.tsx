import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  fallback: ["Geist", "Mona Sans", "IBM Plex Sans", "Manrope", "system-ui", "sans-serif"],
})

export const metadata: Metadata = {
  title: "RAG Chat App",
  description: "Chat with your documents",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  )
}

