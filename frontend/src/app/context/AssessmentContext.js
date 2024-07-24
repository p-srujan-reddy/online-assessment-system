// src/app/context/AssessmentContext.js
"use client";

import { createContext, useContext, useState } from 'react';

const AssessmentContext = createContext();

export const AssessmentProvider = ({ children }) => {
  const [questions, setQuestions] = useState([]);
  const [assessmentType, setAssessmentType] = useState('mcq');
  const [topic, setTopic] = useState('');

  return (
    <AssessmentContext.Provider value={{ questions, setQuestions, assessmentType, setAssessmentType, topic, setTopic }}>
      {children}
    </AssessmentContext.Provider>
  );
}

export const useAssessment = () => useContext(AssessmentContext);
