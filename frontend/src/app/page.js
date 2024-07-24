// src/app/page.js

import AssessmentForm from './components/AssessmentForm'

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">Welcome to the Online Assessment System</h2>
      <AssessmentForm />
    </div>
  )
}