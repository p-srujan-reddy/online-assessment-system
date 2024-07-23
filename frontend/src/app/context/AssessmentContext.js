// src/app/context/AssessmentContext.js

"use client";

import { createContext, useContext, useState } from 'react';

const AssessmentContext = createContext();

export function AssessmentProvider({ children }) {
  const [questions, setQuestions] = useState([]);

  return (
    <AssessmentContext.Provider value={{ questions, setQuestions }}>
      {children}
    </AssessmentContext.Provider>
  );
}

export function useAssessment() {
  return useContext(AssessmentContext);
}
