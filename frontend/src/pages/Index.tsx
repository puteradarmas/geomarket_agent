
import React from 'react';
import DataAnalysisApp from '@/components/DataAnalysisApp';
import '../index.css'; // Ensure global styles are imported

const Index = () => {
  return (
    <>
      <div className="meteor-container">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="meteor" />
        ))}
      </div>

      <div className="container mx-auto px-16 py-8 bg-transparent rounded-lg shadow-lg">
        <DataAnalysisApp />
      </div>
    </>
  );
};

export default Index;
