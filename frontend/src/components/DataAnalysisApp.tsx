
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import InputForm from './InputForm';
import StatisticsDisplay from './StatisticsDisplay';
import HistoryDisplay from './HistoryDisplay';
import { Loader2 } from 'lucide-react';
import teamLogo from '../assets/team-logo.png';
import { Button } from '@/components/ui/button';

export interface FormData {
  location: { lat: number; lng: number } | null;
  additional_prompt: string;
}

export interface ResultData {
  "cafe_list": string[];
  "longitude": number;
  "latitude": number;
  "address": string;
  "num_of_reviews": number;
  "avg_review_score": number;
  "suggestion":string;
  "additional_prompt": string;
}

export interface HistoryEntry {
  "id": number;
  "lat": number;
  "lgn": number;
  "address": string;
  "created_at": string;
};

export interface HistData {
  list: HistoryEntry[];
};
  
const DataAnalysisApp = () => {
  const [formData, setFormData] = useState<FormData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [resultData, setResult] = useState<ResultData | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyData, setHistoryData] = useState<HistData | null>(null);

  const handleShowHistory = async () => {

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/get_history/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        }
      });
  
      if (!response.ok) throw new Error("Network response was not ok");
  
      const result_hist = await response.json();
      setHistoryData(result_hist.message.hist_data);
      console.log("Received from Django:", result_hist);
    } catch (err) {
      console.error("Failed to send data:", err);
    }

    setIsLoading(false);
    setShowHistory(true);
  };

  const handleViewHistory = async (id:number) => {
    setIsLoading(true);
    setShowHistory(false);
    setShowResults(false);
    setFormData(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/view_history/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id }), // 👈 send id in request body
      });
  
      const data = await response.json();
      setResult(data.message);
      console.log("View API response:", data);
    } catch (error) {
      console.error("Failed to call API:", error);
    }  

    // Fetch history data again using DB

    setShowResults(true);
    setIsLoading(false);
  }

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
          Your Geo Market Analysis is just a few clicks away!
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

      {!showResults && !isLoading && !showHistory &&(
        <>
          <InputForm onExecute={handleExecute} onShowHistory={handleShowHistory} />
        </>
      )}

      {showResults && !isLoading && resultData&&(
        <div className="space-y-8">
          <StatisticsDisplay formData={formData} resultData={resultData} onReset={handleReset} />
        </div>
      )}

      {showHistory && !isLoading && (
        <div className="space-y-8">
          <HistoryDisplay HistData={historyData} onViewHistory={handleViewHistory} />
        </div>
      )}
    </div>
  );
};

export default DataAnalysisApp;
