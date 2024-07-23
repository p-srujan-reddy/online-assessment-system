// src/app/components/QuestionList.js
"use client";

import React, { useState } from 'react';
import { useAssessment } from '../context/AssessmentContext';

const QuestionList = () => {
  const { questions } = useAssessment();
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [resetKey, setResetKey] = useState(0); // Key to force re-render

  const handleOptionChange = (questionIndex, optionIndex) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: optionIndex,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let calculatedScore = 0;

    questions.forEach((question, questionIndex) => {
      if (questions[questionIndex].options[selectedAnswers[questionIndex]] === questions[questionIndex].correct_answer) {
        calculatedScore += 1;
      }
    });

    setScore(calculatedScore);
    setShowResults(true);
  };

  const handleReattempt = () => {
    setSelectedAnswers({});
    setShowResults(false);
    setScore(0);
    setResetKey(prevKey => prevKey + 1); // Force re-render
  };

  const getOptionStyle = (questionIndex, optionIndex) => {
    if (!showResults) return '';
    if (questions[questionIndex].options[optionIndex] === questions[questionIndex].correct_answer) {
      return 'bg-green-200';
    }
    if (selectedAnswers[questionIndex] === optionIndex) {
      return 'bg-red-200';
    }
    return '';
  };

  return (
    <div className="max-w-3xl mx-auto mt-8 p-6 bg-white rounded-lg shadow-md" key={resetKey}>
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Generated Questions</h2>
      {showResults && (
        <div className="mb-4 p-4 bg-blue-100 rounded-md text-blue-800">
          <h3 className="text-xl font-semibold">Your Score: {score} / {questions.length}</h3>
        </div>
      )}
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
                    <p className="text-sm text-green-600"><strong>Correct Answer:</strong> {question.correct_answer}</p>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
        {!showResults ? (
          <button
            type="submit"
            className="mt-6 w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Submit Answers
          </button>
        ) : (
          <button
            type="button"
            onClick={handleReattempt}
            className="mt-6 w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Reattempt Assessment
          </button>
        )}
      </form>
    </div>
  );
};

export default QuestionList;
