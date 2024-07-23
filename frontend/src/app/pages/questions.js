// src/app/pages/questions.js

"use client";

import { useAssessment } from '../context/AssessmentContext';
import QuestionList from '../components/QuestionList';

const QuestionsPage = () => {
  const { questions } = useAssessment();

  return (
    <div>
      <h1>Generated Questions</h1>
      <QuestionList questions={questions} />
      <button type="submit" className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
        Submit Answers
      </button>
    </div>
  );
};

export default QuestionsPage;
