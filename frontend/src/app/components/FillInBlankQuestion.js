// src/app/components/FillInBlankQuestion.js
import React from 'react';

const FillInBlankQuestion = ({ question, questionIndex, handleInputChange, selectedAnswer = [], showResults, isCorrect = [], explanation }) => {
  // Determine the style of each input field based on correctness
  const getInputStyle = (index) => {
    if (!showResults) return '';
    return isCorrect[index] ? 'bg-green-200' : 'bg-red-200';
  };

  // Handle changes to input fields
  const handleChange = (index, value) => {
    const newAnswers = [...selectedAnswer];
    newAnswers[index] = value;
    handleInputChange(questionIndex, newAnswers);
  };

  // Split the question text into parts and create input fields for blanks
  const questionParts = question.text.split(/(_+)/g).map((part, i) => {
    const isBlank = i % 2 === 1; // Identify if part is a blank
    const index = Math.floor(i / 2);

    if (isBlank) {
      return (
        <input
          key={`blank-${index}`}
          type="text"
          value={selectedAnswer[index] || ''}
          onChange={(e) => handleChange(index, e.target.value)}
          className={`inline-block mx-1 p-2 border rounded-md ${getInputStyle(index)}`}
          disabled={showResults}
        />
      );
    } else {
      return part;
    }
  });

  // Ensure isCorrect is an array before using .every
  const allCorrect = Array.isArray(isCorrect) ? isCorrect.every(Boolean) : isCorrect;

  return (
    <div className="mb-4 p-4 border border-gray-300 rounded-md">
      <p className="mb-2 font-semibold">
        {questionParts}
      </p>
      {showResults && (
        <div className="mt-2">
          <p className={`text-sm ${allCorrect ? 'text-green-600' : 'text-red-600'}`}>
            {allCorrect ? 'All correct!' : 'Some answers are incorrect!'}
          </p>
          <p className="text-lg font-small">Correct answers: {question.correct_answer}</p>
          <p className="text-sm text-gray-600">{explanation}</p> {/* Display explanation */}
        </div>
      )}
    </div>
  );
};

export default FillInBlankQuestion;