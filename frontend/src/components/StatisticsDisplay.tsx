
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { ResultData,FormData } from './DataAnalysisApp';
import ReactMarkdown from "react-markdown";
import { TrendingUp, DollarSign, MapPin, Target } from 'lucide-react';
import remarkGfm from 'remark-gfm';
import '@/Markdown.css';


interface StatisticsDisplayProps {
  formData: FormData;
  resultData: ResultData;
  onReset: () => void;
}

const StatisticsDisplay: React.FC<StatisticsDisplayProps> = ({ formData,resultData, onReset }) => {
  // Mock data based on form inputs
  const inputData = [
    { name: 'Longitude', value: resultData.longitude },
    { name: 'Latitude', value: resultData.latitude },
  ];

  const address = resultData.address || 'Default theme';


  const prompt_theme = resultData.additional_prompt || 'Default theme';

  // const GeoStats = [
  //   { name: 'Num of Reviews', value: resultData.num_of_reviews },
  //   { name: 'Avg. Review Score', value: resultData.avg_review_score },
  // ];

  const suggestion =  resultData.suggestion || 'No suggestions available';

  const request_id = resultData.request_id || 'No request ID available';

  const handleDownload = () => {
  const fileUrl = "/reccommendation_result/reccommendation_output_"+request_id+".pdf";
  const link = document.createElement("a");
  link.href = fileUrl;
  link.setAttribute("download", "reccommendation_output_"+request_id+".pdf");
  document.body.appendChild(link);
  link.click();
  link.remove();
  };

  // const handleDownload = () => {
  //   const link = document.createElement('a');
  //   link.href = 'http://localhost:8000/download';
  //   link.setAttribute('download', 'llm_output.pdf');
  //   document.body.appendChild(link);
  //   link.click();
  //   document.body.removeChild(link);
  // };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-100">Analysis Results</h2>
        <Button onClick={onReset} variant="outline" className="hover:bg-gray-50">
          New Analysis
        </Button>
      </div>

      {/* Key Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-2 gap-2">
        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardContent className="p-4">
            {inputData.map((data, index) => {
              return (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="text-1x1 font-medium text-gray-600">{data.name}</p>
                    <p className="text-1xl font-bold text-gray-900 mt-1">{data.value}</p>
                  </div>
                </div>
                );
              })}
              <div>
                <p className="text-lg font-medium text-gray-600 mt-4">Address</p>
                <p className="text-sm font-bold text-gray-900 mt-1">{address}</p>
              </div>
          </CardContent>
        </Card>

        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardContent className="p-4">
              <div>
                <p className="text-lg font-medium text-gray-600">Prompt</p>
                <p className="text-mm font-bold text-gray-900 mt-1">{prompt_theme}</p>
              </div>
          </CardContent>
        </Card>
         
        
      </div>
{/* 
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-2">
        {GeoStats.map((data, index) => {
          return (
            <Card className="transition-all duration-200 hover:shadow-lg">
              <CardContent className="p-4">
                    <div key={index} className="flex items-center justify-between">
                      <div>
                        <p className="text-1x1 font-medium text-gray-600">{data.name}</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">{data.value}</p>
                      </div>
                    </div>
              </CardContent>
            </Card>);
          })}  
      </div> */}

      <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-1 gap-2">
        <Card className="transition-all duration-200 hover:shadow-lg w-full">
          <CardContent className="p-4 space-y-1 break-words whitespace-pre-wrap">
              <p className="text-1x1 font-medium text-gray-600 mb-2">Analysis and Recommendation</p>
              {/* <p className="whitespace-pre-line text-sm font-bold text-gray-900 mt-1">{suggestion}</p> */}
              <div className='markdown max-w-3xl'>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{suggestion}</ReactMarkdown>
              </div>
          </CardContent>
        </Card>;
      </div>



      <div className="flex justify-between items-center">
        <Button onClick={handleDownload} variant="outline" className="hover:bg-gray-50">
          Download Report
        </Button>
      </div>

    </div>
  );
};

export default StatisticsDisplay;
