// src/app/components/QuestionList.js

"use client";

import React, { useEffect, useState } from 'react';
import { useAssessment } from '../context/AssessmentContext';
import { useRouter } from 'next/navigation';

const QuestionList = () => {
  const { questions } = useAssessment();
  const [submitted, setSubmitted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (submitted) {
      router.push('/results');
    }
  }, [submitted, router]);

  const handleSubmit = () => {
    setSubmitted(true);
  };

  return (
    <div>
      <h2>Generated Questions</h2>
      <ul>
        {questions.map((question, index) => (
          <li key={index}>{question}</li>
        ))}
      </ul>
      <button
        onClick={handleSubmit}
        className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Submit Answers
      </button>
    </div>
  );
};

export default QuestionList;
