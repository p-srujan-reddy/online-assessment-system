// src/app/components/DocumentUpload.js
import React, { useState, useContext } from 'react';
import { useAssessment } from '../context/AssessmentContext';

const DocumentUpload = () => {
  const { setAssessmentData } = useAssessment();
  const [file, setFile] = useState(null);
  const [topic, setTopic] = useState('general');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTopicChange = (e) => {
    setTopic(e.target.value);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('topic', topic);

    const response = await fetch('/upload-document/', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();
    setAssessmentData(result.data);
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <input type="text" value={topic} onChange={handleTopicChange} placeholder="Topic" />
      <button onClick={handleUpload}>Upload Document</button>
    </div>
  );
};

export default DocumentUpload;
