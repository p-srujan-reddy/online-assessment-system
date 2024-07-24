// src/app/components/ShortAnswerQuestion.js
import React from 'react';

const ShortAnswerQuestion = ({ question, questionIndex, handleInputChange, selectedAnswer, showResults, isCorrect, verifiedByLLM }) => {
  return (
    <div className={`p-4 mb-4 border ${showResults ? (isCorrect ? 'bg-green-100 border-green-300' : 'bg-red-100 border-red-300') : 'border-gray-300'}`}>
      <p className="text-lg font-medium">{question.text}</p>
      <textarea
        className={`mt-2 p-2 w-full border rounded-md ${showResults ? (isCorrect ? 'bg-green-50' : 'bg-red-50') : 'border-gray-300'}`}
        value={selectedAnswer || ''}
        onChange={(e) => handleInputChange(questionIndex, e.target.value)}
        disabled={showResults}
      />
      {showResults && (
        <div className="mt-2">
          <p className={`text-sm ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
            {isCorrect ? 'Correct!' : 'Incorrect!'}
          </p>
          <p className="text-sm font-medium text-gray-700">
            <strong>Correct Answer:</strong> {question.correct_answer}
          </p>
          {verifiedByLLM && (
            <p className="text-sm text-gray-600">
              Verified by LLM
            </p>
          )}
          {!verifiedByLLM && (
            <p className="text-sm text-gray-600">
              Not verified by LLM
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ShortAnswerQuestion;
