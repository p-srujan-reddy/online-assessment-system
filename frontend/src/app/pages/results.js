// src/app/pages/results.js
import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import AnswerForm from '../components/AnswerForm';

const Results = () => {
  const questions = []; // Fetch questions from the backend

  return (
    <div>
      <Header />
      <main>
        <AnswerForm questions={questions} />
      </main>
      <Footer />
    </div>
  );
};

export default Results;
