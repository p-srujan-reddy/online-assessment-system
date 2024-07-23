// src/app/components/QuestionList.js
"use client";

import React, { useState } from 'react';
import { useAssessment } from '../context/AssessmentContext';

const QuestionList = () => {
  const { questions, assessmentType } = useAssessment();
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);

  const handleOptionChange = (questionIndex, optionIndex) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: optionIndex,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowResults(true);
  };

  const getOptionStyle = (questionIndex, optionIndex) => {
    if (!showResults) return '';
    if (questions[questionIndex].correctAnswerIndex === optionIndex) {
      return 'bg-green-200';
    }
    if (selectedAnswers[questionIndex] === optionIndex) {
      return 'bg-red-200';
    }
    return '';
  };

  return (
    <div className="max-w-3xl mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Generated Questions</h2>
      <form onSubmit={handleSubmit}>
        <ul className="space-y-6">
          {questions.map((question, questionIndex) => (
            <li key={questionIndex} className="p-4 bg-gray-50 rounded-lg shadow-sm">
              <div>
                <p className="font-semibold">{question.text}</p>
                {question.options.map((option, optionIndex) => (
                  <div key={optionIndex} className={`p-2 rounded ${getOptionStyle(questionIndex, optionIndex)}`}>
                    <label className="flex items-center space-x-2">
                      <input
                        type="radio"
                        name={`question-${questionIndex}`}
                        value={option}
                        checked={selectedAnswers[questionIndex] === optionIndex}
                        onChange={() => handleOptionChange(questionIndex, optionIndex)}
                        className="form-radio h-4 w-4 text-indigo-600"
                      />
                      <span>{option}</span>
                    </label>
                  </div>
                ))}
                {showResults && (
                  <div className="mt-2">
                    <p className="text-sm text-green-600"><strong>Correct Answer:</strong> {question.correctAnswer}</p>
                    <p className="text-sm text-gray-600"><strong>Explanation:</strong> {question.explanation}</p>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
        {!showResults && (
          <button
            type="submit"
            className="mt-6 w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Submit Answers
          </button>
        )}
      </form>
    </div>
  );
};

export default QuestionList;
