// src/app/components/LoadingSpinner.js

const LoadingSpinner = () => {
    return (
      <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
    );
  };
  
  export default LoadingSpinner;
  