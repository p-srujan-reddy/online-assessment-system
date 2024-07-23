// src/app/ClientLayout.js

"use client";

import { AssessmentProvider } from './context/AssessmentContext';

export default function ClientLayout({ children }) {
  return (
    <AssessmentProvider>
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
    </AssessmentProvider>
  );
}
