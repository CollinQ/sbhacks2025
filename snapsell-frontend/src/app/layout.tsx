import './globals.css'
import { Inter } from 'next/font/google'
import { Tabs } from '../components/Tabs'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'SnapSell',
  description: 'Quickly create and manage marketplace listings from video input',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-100">
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
              <h1 className="text-3xl font-bold text-gray-900">SnapSell</h1>
            </div>
          </header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Tabs />
          </div>
          <main>
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}
