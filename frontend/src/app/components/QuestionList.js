// src/app/components/QuestionList.js
import React from 'react';

const QuestionList = ({ questions, setQuestions }) => {
  const handleScoreChange = (index, score) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index].score = score;
    setQuestions(updatedQuestions);
  };

  return (
    <div>
      <h2>Generated Questions</h2>
      <ul>
        {questions.map((question, index) => (
          <li key={index}>
            <p>{question.text}</p>
            <label>Score:</label>
            <input
              type="number"
              value={question.score || 0}
              onChange={(e) => handleScoreChange(index, e.target.value)}
            />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default QuestionList;
