// src/app/components/MCQQuestion.js

import React from 'react';

const MCQQuestion = ({ question, questionIndex, handleInputChange, selectedAnswer, showResults }) => {
  const getOptionStyle = (optionIndex) => {
    if (!showResults) return '';
    if (question.options[optionIndex] === question.correct_answer) {
      return 'bg-green-200';
    }
    if (selectedAnswer === question.options[optionIndex]) {
      return 'bg-red-200';
    }
    return '';
  };

  return (
    <div className="mb-4 p-4 border border-gray-300 rounded-md">
      <p className="mb-2 font-semibold">{question.text}</p>
      <div className="space-y-2">
        {question.options.map((option, optionIndex) => (
          <div key={optionIndex} className={`p-2 rounded-md ${getOptionStyle(optionIndex)}`}>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name={`question-${questionIndex}`}
                value={option}
                onChange={() => handleInputChange(questionIndex, option)}
                checked={selectedAnswer === option}
                className="mr-2"
                disabled={showResults}
              />
              {option}
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MCQQuestion;
