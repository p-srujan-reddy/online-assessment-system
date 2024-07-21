import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Online Assessment System',
  description: 'LLM-powered assessment generation and evaluation',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-100`}>
        <header className="bg-indigo-600 text-white p-4">
          <div className="container mx-auto">
            <h1 className="text-2xl font-bold">Online Assessment System</h1>
          </div>
        </header>
        <main className="container mx-auto mt-8 p-4">
          {children}
        </main>
        <footer className="bg-gray-200 p-4 mt-8">
          <div className="container mx-auto text-center text-gray-600">
            <p>&copy; 2024 Online Assessment System</p>
          </div>
        </footer>
      </body>
    </html>
  )
}