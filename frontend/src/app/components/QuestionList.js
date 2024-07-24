// src/app/components/QuestionList.js
"use client";

import React, { useState } from 'react';
import { useAssessment } from '../context/AssessmentContext';
import { scoreAnswers } from '../../../lib/api';
import MCQQuestion from './MCQQuestion';
import ShortAnswerQuestion from './ShortAnswerQuestion';

const QuestionList = () => {
  const { questions, assessmentType, topic } = useAssessment();
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [resetKey, setResetKey] = useState(0);

  const handleInputChange = (questionIndex, value) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    if (assessmentType === 'mcq') {
      // Calculate score for MCQs on the client side
      let calculatedScore = 0;
      questions.forEach((question, questionIndex) => {
        if (selectedAnswers[questionIndex] === question.correct_answer) {
          calculatedScore += 1;
        }
      });
  
      setScore(calculatedScore);
      setShowResults(true);
    } else {
      // For short answer questions, send the answers to the backend for scoring
      const answers = questions.map((question, questionIndex) => ({
        type: question.type,
        text: question.text,
        user_answer: selectedAnswers[questionIndex] || '',
      }));
  
      try {
        const result = await scoreAnswers({ answers, topic });
        setScore(result.total_score);
        setShowResults(true);
      } catch (error) {
        console.error('Error scoring answers:', error);
      }
    }
  };
  
  const handleReattempt = () => {
    setSelectedAnswers({});
    setShowResults(false);
    setScore(0);
    setResetKey((prevKey) => prevKey + 1);
  };

  return (
    <div className="mt-8">
      <form onSubmit={handleSubmit} key={resetKey}>
        {questions.map((question, questionIndex) => (
          <div key={questionIndex}>
            {question.type === 'mcq' ? (
              <MCQQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
              />
            ) : (
              <ShortAnswerQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
              />
            )}
          </div>
        ))}
        {!showResults && (
          <button
            type="submit"
            className="mt-4 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Submit Answers
          </button>
        )}
      </form>
      {showResults && (
        <div className="mt-4">
          <p className="text-lg font-medium">
            Your Score: {score} / {questions.length}
          </p>
          <button
            onClick={handleReattempt}
            className="mt-2 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Reattempt
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionList;
