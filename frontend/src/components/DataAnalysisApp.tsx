
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import InputForm from './InputForm';
import StatisticsDisplay from './StatisticsDisplay';
import DataTable from './DataTable';
import { Loader2 } from 'lucide-react';

export interface FormData {
  location: string;
  theme: string;
  budget: number;
  category: string;
  timeframe: string;
  priority: string;
}

const DataAnalysisApp = () => {
  const [formData, setFormData] = useState<FormData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleExecute = async (data: FormData) => {
    setIsLoading(true);
    setFormData(data);
    console.log('Executing analysis with data:', data);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsLoading(false);
    setShowResults(true);
  };

  const handleReset = () => {
    setShowResults(false);
    setFormData(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Data Analysis Dashboard
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Enter your parameters to generate comprehensive analytics and insights
        </p>
      </div>

      {isLoading && (
        <Card className="mb-8">
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-lg font-medium text-gray-700">
                Processing your request...
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Analyzing data and generating insights
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {!showResults && !isLoading && (
        <InputForm onExecute={handleExecute} />
      )}

      {showResults && !isLoading && formData && (
        <div className="space-y-8">
          <StatisticsDisplay formData={formData} onReset={handleReset} />
          <DataTable formData={formData} />
        </div>
      )}
    </div>
  );
};

export default DataAnalysisApp;
