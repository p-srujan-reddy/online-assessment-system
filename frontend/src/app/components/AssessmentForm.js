// src/app/components/AssessmentForm.js

"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { generateAssessment, uploadDocument } from '../../../lib/api';
import LoadingSpinner from './LoadingSpinner';
import { useAssessment } from '../context/AssessmentContext';
import Cookies from 'js-cookie';


export default function AssessmentForm() {
  const [topic, setTopic] = useState('');
  const [assessmentType, setAssessmentType] = useState('mcq');
  const [questionCount, setQuestionCount] = useState(5);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { setQuestions, setAssessmentType: setContextAssessmentType, setTopic: setContextTopic } = useAssessment();

  const handleFileSelect = (event) => {
    setFiles(event.target.files);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Upload documents
      const uploadPromises = Array.from(files).map(file => uploadDocument(file, topic));
      await Promise.all(uploadPromises);

      // Generate assessment
      const data = await generateAssessment({ topic, assessmentType, questionCount });
      setQuestions(data.questions);
      setContextAssessmentType(assessmentType);
      setContextTopic(topic);
      router.push('/questions');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Generate Assessment</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Topic Selection */}
        <div>
          <label htmlFor="topic" className="block text-sm font-medium text-gray-700">Topic</label>
          <input
            type="text"
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter topic"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          />
        </div>

        {/* Assessment Type */}
        <div>
          <label htmlFor="assessmentType" className="block text-sm font-medium text-gray-700">Assessment Type</label>
          <select
            id="assessmentType"
            value={assessmentType}
            onChange={(e) => setAssessmentType(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          >
            <option value="mcq">Multiple Choice</option>
            <option value="true_false">True or False</option>
            <option value="fill_in_blank">Fill in the Blank</option>
            <option value="short_answer">Short Answer</option>
            <option value="long_answer">Long Answer</option>
          </select>
        </div>

        {/* Number of Questions */}
        <div>
          <label htmlFor="questionCount" className="block text-sm font-medium text-gray-700">Number of Questions</label>
          <input
            type="number"
            id="questionCount"
            value={questionCount}
            onChange={(e) => setQuestionCount(parseInt(e.target.value))}
            min="1"
            max="20"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          />
        </div>

        {/* Upload Documents */}
        <div>
          <label htmlFor="documents" className="block text-sm font-medium text-gray-700">Upload Documents</label>
          <input
            type="file"
            id="documents"
            multiple
            onChange={handleFileSelect}
            className="mt-1 block w-full"
          />
        </div>

        {/* Submit Button */}
        <button type="submit" className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          {loading ? <LoadingSpinner /> : 'Generate Assessment'}
        </button>
      </form>
    </div>
  );
}