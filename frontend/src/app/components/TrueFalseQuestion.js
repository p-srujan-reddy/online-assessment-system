// src/app/components/TrueFalseQuestion.js
import React from 'react';

const TrueFalseQuestion = ({ question, questionIndex, handleInputChange, selectedAnswer, showResults }) => {
  const getOptionStyle = (option) => {
    if (!showResults) return '';
    if (option === question.correct_answer) {
      return 'bg-green-200';
    }
    if (selectedAnswer === option) {
      return 'bg-red-200';
    }
    return '';
  };

  return (
    <div className="mb-4 p-4 border border-gray-300 rounded-md">
      <p className="mb-2 font-semibold">{question.text}</p>
      <div className="space-y-2">
        {['True', 'False'].map((option) => (
          <div key={option} className={`p-2 rounded-md ${getOptionStyle(option)}`}>
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

export default TrueFalseQuestion;
