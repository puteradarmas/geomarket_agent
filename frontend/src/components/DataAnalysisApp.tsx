
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import InputForm from './InputForm';
import StatisticsDisplay from './StatisticsDisplay';
import DataTable from './DataTable';
import { Loader2 } from 'lucide-react';
import teamLogo from '../assets/team-logo.png';

export interface FormData {
  location: { lat: number; lng: number } | null;
  additional_prompt: string;
  budget: number;
}

export interface ResultData {
  "cafe_list": string[];
  "longitude": number;
  "latitude": number;
  "opportunities_list": string[];
  "num_of_reviews": number;
  "avg_review_score": number;
  "suggestion1":string;
  "suggestion2":string;
  "suggestion3":string;
}

export interface HistResult {
  "id": Int16Array[];
  "lat": number[];
  "lgn": number[];
  "address": string[];
}
  
const DataAnalysisApp = () => {
  const [formData, setFormData] = useState<FormData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [resultData, setResult] = useState<ResultData | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleShowHistory = async () => {

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/analyze/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        }
      });
  
      if (!response.ok) throw new Error("Network response was not ok");
  
      const HistResult = await response.json();
      setResult(HistResult.message);
      console.log("Received from Django:", HistResult);
    } catch (err) {
      console.error("Failed to send data:", err);
    }

    setIsLoading(false);
    setShowHistory(true);
  };

  const handleExecute = async (data: FormData) => {
    setIsLoading(true);
    setFormData(data);
    console.log('Executing analysis with data:', data);

    
    try {
      const response = await fetch("http://localhost:8000/api/analyze/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
  
      if (!response.ok) throw new Error("Network response was not ok");
  
      const result = await response.json();
      setResult(result.message);
      console.log("Received from Django:", result);
    } catch (err) {
      console.error("Failed to send data:", err);
    }
    
    setIsLoading(false);
    setShowResults(true);
  };

  const handleReset = () => {
    setShowResults(false);
    setFormData(null);
  };

  return (
    <div className="container mx-auto px-4 py-8 bg-white/10 backdrop-blur-md/50 rounded-lg shadow-lg">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-4 mb-4">
          <img src={teamLogo} alt="Logo" className="logo-icon" />
          <h1 className="text-4xl font-bold text-gray-300">
            Geo Analytical Survey
          </h1>
        </div>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
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
        // add show history button
      )}

      {showResults && !isLoading && formData && resultData&&(
        <div className="space-y-8">
          <StatisticsDisplay formData={formData} resultData={resultData} onReset={handleReset} />
          {/* <DataTable formData={formData} /> */}
        </div>
      )}

      {showHistory && !isLoading && (
        <div className="space-y-8">
          <StatisticsDisplay formData={formData} resultData={resultData} onReset={handleReset} />
          {/* <DataTable formData={formData} /> */}
        </div>
      )}
    </div>
  );
};

export default DataAnalysisApp;
