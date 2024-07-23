// src/app/context/AssessmentContext.js

"use client";

import { createContext, useContext, useState } from 'react';

const AssessmentContext = createContext();

export function AssessmentProvider({ children }) {
  const [questions, setQuestions] = useState([]);
  const [assessmentType, setAssessmentType] = useState('mcq');

  return (
    <AssessmentContext.Provider value={{ questions, setQuestions, assessmentType, setAssessmentType }}>
      {children}
    </AssessmentContext.Provider>
  );
}

export function useAssessment() {
  return useContext(AssessmentContext);
}
