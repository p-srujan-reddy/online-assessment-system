// src/app/components/AnswerForm.js
import React, { useState } from 'react';

const AnswerForm = ({ questions }) => {
  const [answers, setAnswers] = useState(questions.map(() => ''));

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Call the backend API to submit answers and get scores
    const response = await fetch('/api/submit-answers', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ answers }),
    });
    const data = await response.json();
    // Handle the response data (e.g., show scores)
  };

  const handleAnswerChange = (index, answer) => {
    const updatedAnswers = [...answers];
    updatedAnswers[index] = answer;
    setAnswers(updatedAnswers);
  };

  return (
    <form onSubmit={handleSubmit}>
      <ul>
        {questions.map((question, index) => (
          <li key={index}>
            <p>{question.text}</p>
            <input
              type="text"
              value={answers[index]}
              onChange={(e) => handleAnswerChange(index, e.target.value)}
              required
            />
          </li>
        ))}
      </ul>
      <button type="submit">Submit Answers</button>
    </form>
  );
};

export default AnswerForm;
