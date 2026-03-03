import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800', '900'],
  display: 'swap',
  preload: false,
})

export const metadata: Metadata = {
  title: 'AudioScript – Audio to Text Transcription',
  description:
    'Upload any audio or video file and get an accurate transcript in seconds. Powered by OpenAI Whisper. 99 languages. Fully private.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
