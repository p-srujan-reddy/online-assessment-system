// src/app/components/ShortAnswerQuestion.js

import React from 'react';

const ShortAnswerQuestion = ({ question, questionIndex, handleInputChange, selectedAnswer, showResults }) => {
  return (
    <div className="mb-4 p-4 border border-gray-300 rounded-md">
      <p className="mb-2 font-semibold">{question.text}</p>
      <input
        type="text"
        name={`question-${questionIndex}`}
        value={selectedAnswer || ''}
        onChange={(e) => handleInputChange(questionIndex, e.target.value)}
        className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        disabled={showResults}
      />
      {showResults && (
        <p className="mt-2 text-sm text-gray-500">
          Correct Answer: {question.correct_answer}
        </p>
      )}
    </div>
  );
};

export default ShortAnswerQuestion;
