// src/app/components/QuestionList.js
"use client";

import React, { useState } from 'react';
import { useAssessment } from '../context/AssessmentContext';
import { scoreShortAnswers, scoreLongAnswers, scoreFillInTheBlanks } from '../../../lib/api';
import MCQQuestion from './MCQQuestion';
import ShortAnswerQuestion from './ShortAnswerQuestion';
import TrueFalseQuestion from './TrueFalseQuestion';
import FillInBlankQuestion from './FillInBlankQuestion';
import LongAnswerQuestion from './LongAnswerQuestion';

const QuestionList = () => {
  const { questions, assessmentType, topic } = useAssessment();
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [resetKey, setResetKey] = useState(0);
  const [results, setResults] = useState([]);

  const handleInputChange = (questionIndex, value) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    let calculatedScore = 0;
    const answersToScore = [];

    questions.forEach((question, questionIndex) => {
      const userAnswer = selectedAnswers[questionIndex] || '';
      const correctAnswer = question.correct_answer;
      let isCorrect = false;

      if (question.type === 'mcq' || question.type === 'true_false') {
        isCorrect = userAnswer === correctAnswer;
        calculatedScore += isCorrect ? 1 : 0;
      } else {
        answersToScore.push({
          type: question.type,
          text: question.text,
          user_answer: userAnswer,
          correct_answer: correctAnswer,
        });
      }

      results[questionIndex] = { is_correct: isCorrect };
    });

    setScore(calculatedScore);

    if (answersToScore.length > 0) {
      try {
        const fillInBlankAnswers = answersToScore.filter(answer => answer.type === 'fill_in_blank');
        const otherAnswers = answersToScore.filter(answer => answer.type !== 'fill_in_blank');

        if (fillInBlankAnswers.length > 0) {
          const fillInBlankResult = await scoreFillInTheBlanks({ answers: fillInBlankAnswers, topic });
          fillInBlankResult.detailed_results.forEach((res, idx) => {
            const index = questions.findIndex(q => q.text === fillInBlankAnswers[idx].text);
            results[index] = res;
            calculatedScore += res.is_correct ? 1 : 0;
          });
        }

        if (otherAnswers.length > 0) {
          const result = await scoreShortAnswers({ answers: otherAnswers, topic });
          result.detailed_results.forEach((res, idx) => {
            const index = questions.findIndex(q => q.text === otherAnswers[idx].text);
            results[index] = res;
            calculatedScore += res.is_correct ? 1 : 0;
          });
        }

        setScore(calculatedScore);
      } catch (error) {
        console.error('Error scoring answers:', error);
      }
    }

    setResults(results);
    setShowResults(true);
  };

  const handleReattempt = () => {
    setSelectedAnswers({});
    setShowResults(false);
    setScore(0);
    setResetKey((prevKey) => prevKey + 1);
    setResults([]);
  };

  return (
    <div className="mt-8">
      <form onSubmit={handleSubmit} key={resetKey}>
        {questions.map((question, questionIndex) => (
          <div key={questionIndex}>
            {question.type === 'mcq' && (
              <MCQQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
              />
            )}
            {question.type === 'true_false' && (
              <TrueFalseQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
              />
            )}
            {question.type === 'fill_in_blank' && (
              <FillInBlankQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
                isCorrect={results[questionIndex]?.is_correct}
                explanation={results[questionIndex]?.explanation} // Added explanation prop
              />
            )}
            {question.type === 'short_answer' && (
              <ShortAnswerQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
                isCorrect={results[questionIndex]?.is_correct}
                verifiedByLLM={results[questionIndex]?.verified_by_llm}
                explanation={results[questionIndex]?.explanation} // Added explanation prop
              />
            )}
            {question.type === 'long_answer' && (
              <LongAnswerQuestion
                question={question}
                questionIndex={questionIndex}
                handleInputChange={handleInputChange}
                selectedAnswer={selectedAnswers[questionIndex]}
                showResults={showResults}
                isCorrect={results[questionIndex]?.is_correct}
                verifiedByLLM={results[questionIndex]?.verified_by_llm}
                explanation={results[questionIndex]?.explanation} // Added explanation prop
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