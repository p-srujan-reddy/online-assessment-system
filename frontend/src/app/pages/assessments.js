// src/app/pages/assessments.js
import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import AssessmentForm from '../components/AssessmentForm';
import QuestionList from '../components/QuestionList';

const Assessments = () => {
  const [questions, setQuestions] = useState([]);

  return (
    <div>
      <Header />
      <main>
        <AssessmentForm onQuestionsGenerated={setQuestions} />
        <QuestionList questions={questions} setQuestions={setQuestions} />
      </main>
      <Footer />
    </div>
  );
};

export default Assessments;
