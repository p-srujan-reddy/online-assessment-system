// src/app/layout.js

import './globals.css';
import { Inter } from 'next/font/google';
import ClientLayout from './ClientLayout';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Online Assessment System',
  description: 'LLM-powered assessment generation and evaluation',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-100`}>
        <ClientLayout>
          {children}
        </ClientLayout>
      </body>
    </html>
  );
}
