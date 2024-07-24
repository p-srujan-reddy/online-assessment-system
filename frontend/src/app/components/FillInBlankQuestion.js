import React from 'react';

const FillInBlankQuestion = ({ question, questionIndex, handleInputChange, selectedAnswers = [], showResults, isCorrect = [] }) => {
  // Determine the style of each input field based on correctness
  const getInputStyle = (index) => {
    if (!showResults) return '';
    return isCorrect[index] ? 'bg-green-200' : 'bg-red-200';
  };

  // Handle changes to input fields
  const handleChange = (index, value) => {
    const newAnswers = [...selectedAnswers];
    newAnswers[index] = value;
    handleInputChange(questionIndex, newAnswers);
  };

  // Split the question text into parts and create input fields for blanks
  const questionParts = question.text.split(/(_+)/g).map((part, i) => {
    const isBlank = i % 2 === 1; // Identify if part is a blank
    const index = Math.floor(i / 2);

    return isBlank ? (
      <input
        key={`blank-${index}`}
        type="text"
        value={selectedAnswers[index] || ''}
        onChange={(e) => handleChange(index, e.target.value)}
        className={`inline-block mx-1 p-2 border rounded-md ${getInputStyle(index)}`}
        disabled={showResults}
      />
    ) : (
      part
    );
  });

  return (
    <div className="mb-4 p-4 border border-gray-300 rounded-md">
      <p className="mb-2 font-semibold">
        {questionParts}
      </p>
      {showResults && (
        <div className="mt-2">
          <p className="text-sm text-gray-600">
            Correct answers: {question.correct_answer}
          </p>
        </div>
      )}
    </div>
  );
};

export default FillInBlankQuestion;
