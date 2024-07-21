// src/app/components/Dashboard.js
import React from 'react';

const Dashboard = ({ role, assessments, performance }) => {
  return (
    <div>
      <h2>Dashboard</h2>
      <ul>
        {role === 'faculty' ? (
          assessments.map((assessment, index) => (
            <li key={index}>
              <p>{assessment.title}</p>
              <p>Created on: {assessment.date}</p>
            </li>
          ))
        ) : (
          performance.map((result, index) => (
            <li key={index}>
              <p>Assessment: {result.assessmentTitle}</p>
              <p>Score: {result.score}</p>
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default Dashboard;
