// src/app/pages/index.js

import AssessmentForm from '../components/AssessmentForm';

export default function Home() {
  return (
    <div>
      <h1 className="text-center text-4xl font-bold my-8">Online Assessment System</h1>
      <AssessmentForm />
    </div>
  );
}
