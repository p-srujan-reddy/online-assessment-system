// src/app/components/QuestionList.js
import React, { useState } from 'react';

const QuestionList = ({ questions }) => {
  const [answers, setAnswers] = useState({});

  const handleAnswerChange = (index, value) => {
    setAnswers({ ...answers, [index]: value });
  };

  const handleSubmit = () => {
    console.log('Submitted Answers:', answers);
    // Here, you can send the answers to your backend for processing.
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Answer the Questions</h2>
      <form className="space-y-4">
        {questions.map((question, index) => (
          <div key={index}>
            <p className="text-sm font-medium text-gray-700">{question.text}</p>
            {question.options && question.options.length > 0 ? (
              <select
                value={answers[index] || ''}
                onChange={(e) => handleAnswerChange(index, e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              >
                <option value="" disabled>Select an answer</option>
                {question.options.map((option, optIndex) => (
                  <option key={optIndex} value={option}>{option}</option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={answers[index] || ''}
                onChange={(e) => handleAnswerChange(index, e.target.value)}
                placeholder="Enter your answer"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              />
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={handleSubmit}
          className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Submit Answers
        </button>
      </form>
    </div>
  );
};

export default QuestionList;
