// src/app/context/AssessmentContext.js
"use client";

import React, { createContext, useContext, useState } from 'react';

const AssessmentContext = createContext();

export const AssessmentProvider = ({ children }) => {
  const [questions, setQuestions] = useState([]);
  const [assessmentType, setAssessmentType] = useState('mcq');
  const [topic, setTopic] = useState('');
  const [assessmentData, setAssessmentData] = useState(null);

  return (
    <AssessmentContext.Provider value={{
      questions,
      setQuestions,
      assessmentType,
      setAssessmentType,
      topic,
      setTopic,
      assessmentData,
      setAssessmentData,
    }}>
      {children}
    </AssessmentContext.Provider>
  );
}

export const useAssessment = () => useContext(AssessmentContext);
export default AssessmentContext;
