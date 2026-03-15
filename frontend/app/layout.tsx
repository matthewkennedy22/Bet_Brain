import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'BetBrain - AI Sports Betting Analyzer',
  description: 'AI-powered sports betting picks and analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

