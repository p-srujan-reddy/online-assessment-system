// src/app/components/Header.js
import React from 'react';
import Link from 'next/link';

const Header = () => {
  return (
    <header className="bg-blue-500 text-white p-4">
      <div className="container mx-auto">
        <nav className="flex justify-between">
          <div className="text-lg font-bold">Assessment System</div>
          <div>
            <Link href="/" className="px-2">Home</Link>
            <Link href="/assessments" className="px-2">Assessments</Link>
            <Link href="/results" className="px-2">Results</Link>
            <Link href="/admin-dashboard" className="px-2">Admin Dashboard</Link>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Header;
