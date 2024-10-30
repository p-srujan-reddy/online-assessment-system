// src/app/components/LongAnswerQuestion.js
import React, { useRef, useEffect } from 'react';

const LongAnswerQuestion = ({ question, questionIndex, handleInputChange, selectedAnswer, showResults, isCorrect, verifiedByLLM, explanation }) => {
  const textareaRef = useRef(null);

  // Adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height to auto to get new scrollHeight
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Set height to scrollHeight
    }
  }, [selectedAnswer]);

  return (
    <div className={`p-4 mb-4 border ${showResults ? (isCorrect ? 'bg-green-100 border-green-300' : 'bg-red-100 border-red-300') : 'border-gray-300'}`}>
      <p className="text-lg font-medium">{question.text}</p>
      <textarea
        ref={textareaRef}
        className={`mt-2 p-2 w-full border rounded-md ${showResults ? (isCorrect ? 'bg-green-50' : 'bg-red-50') : 'border-gray-300'} resize-none`}
        value={selectedAnswer || ''}
        onChange={(e) => handleInputChange(questionIndex, e.target.value)}
        disabled={showResults}
        style={{ minHeight: '100px', overflow: 'hidden' }} // Set a minimum height and hide overflow
      />
      {showResults && (
        <div className="mt-2">
          <p className={`text-sm ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
            {isCorrect ? 'Correct!' : 'Incorrect!'}
          </p>
          <p className="text-lg font-small">{question.correct_answer}</p>
          <p className="text-sm text-gray-600">{verifiedByLLM ? 'Verified by LLM' : 'Not verified by LLM'}</p>
          <p className="text-sm text-gray-700 mt-2">{explanation}</p> {/* Display explanation */}
        </div>
      )}
    </div>
  );
};

export default LongAnswerQuestion;