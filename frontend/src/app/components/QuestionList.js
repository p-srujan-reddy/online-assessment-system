// src/app/components/QuestionList.js

"use client";

import React, { useState } from 'react';
import { useAssessment } from '../context/AssessmentContext';

const QuestionList = () => {
  const { questions, assessmentType } = useAssessment();
  const [selectedAnswers, setSelectedAnswers] = useState({});

  const handleOptionChange = (questionIndex, optionIndex) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: optionIndex,
    });
  };

  return (
    <div>
      <h2>Generated Questions</h2>
      {assessmentType === 'mcq' ? (
        <ul>
          {questions.map((question, questionIndex) => (
            <li key={questionIndex}>
              <div>
                <p>{question.text}</p>
                <form>
                  {question.options.map((option, optionIndex) => (
                    <div key={optionIndex}>
                      <label>
                        <input
                          type="radio"
                          name={`question-${questionIndex}`}
                          value={option}
                          checked={selectedAnswers[questionIndex] === optionIndex}
                          onChange={() => handleOptionChange(questionIndex, optionIndex)}
                        />
                        {option}
                      </label>
                    </div>
                  ))}
                </form>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <ul>
          {questions.map((question, index) => (
            <li key={index}>
              <div>
                <p>{question.text}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default QuestionList;
