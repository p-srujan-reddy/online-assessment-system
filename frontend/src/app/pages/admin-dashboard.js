// src/app/pages/admin-dashboard.js
import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Dashboard from '../components/Dashboard';

const AdminDashboard = () => {
  const role = 'faculty'; // Fetch user role from the backend
  const assessments = []; // Fetch assessments from the backend

  return (
    <div>
      <Header />
      <main>
        <Dashboard role={role} assessments={assessments} performance={[]} />
      </main>
      <Footer />
    </div>
  );
};

export default AdminDashboard;
