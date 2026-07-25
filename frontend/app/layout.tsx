import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Graveyard Mining — AI Project Planning Assistant',
  description: 'Discover abandoned GitHub repositories, analyze failure patterns, and generate risk-annotated project roadmaps.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090D16] text-gray-100 antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  )
}
