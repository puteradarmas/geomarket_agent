
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
  onDownload: () => void;
}

const StatisticsDisplay: React.FC<StatisticsDisplayProps> = ({ formData,resultData, onReset,onDownload }) => {
  // Mock data based on form inputs
  const inputData = [
    { name: 'Longitude', value: resultData.longitude },
    { name: 'Latitude', value: resultData.latitude },
  ];

  const address = resultData.address || 'Default theme';


  const prompt_theme = resultData.additional_prompt || 'Default theme';

  const GeoStats = [
    { name: 'Num of Reviews', value: resultData.num_of_reviews },
    { name: 'Avg. Review Score', value: resultData.avg_review_score },
  ];

  const suggestion =  resultData.suggestion || 'No suggestions available';

  // const handleDownload = () => {
  //   const link = document.createElement('a');
  //   link.href = 'http://localhost:8000/download';
  //   link.setAttribute('download', 'llm_output.docx');
  //   document.body.appendChild(link);
  //   link.click();
  //   document.body.removeChild(link);
  // };
  // // const stats = [
  //   {
  //     title: 'Total Budget Allocation',
  //     value: `$${formData.budget.toLocaleString()}`,
  //     icon: DollarSign,
  //     color: 'text-green-600',
  //     bgColor: 'bg-green-100'
  //   },
  //   {
  //     title: 'Target Location',
  //     value: formData.location,
  //     icon: MapPin,
  //     color: 'text-blue-600',
  //     bgColor: 'bg-blue-100'
  //   },
  //   {
  //     title: 'Project Theme',
  //     value: formData.theme,
  //     icon: Target,
  //     color: 'text-purple-600',
  //     bgColor: 'bg-purple-100'
  //   },
  //   {
  //     title: 'Expected ROI',
  //     value: '23.5%',
  //     icon: TrendingUp,
  //     color: 'text-orange-600',
  //     bgColor: 'bg-orange-100'
  //   }
  // ];

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
                    <p className="text-2xl font-bold text-gray-900 mt-1">{data.value}</p>
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
      </div>

      <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-1 gap-2">
        <Card className="transition-all duration-200 hover:shadow-lg w-full">
          <CardContent className="p-4 space-y-2 break-words whitespace-pre-wrap">
              <p className="text-1x1 font-medium text-gray-600">Analysis and Recommendation</p>
              {/* <p className="whitespace-pre-line text-sm font-bold text-gray-900 mt-1">{suggestion}</p> */}
              <div className='markdown'>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{suggestion}</ReactMarkdown>
              </div>
          </CardContent>
        </Card>;
      </div>



      <div className="flex justify-between items-center">
        <Button onClick={onDownload} variant="outline" className="hover:bg-gray-50">
          Download Report
        </Button>
      </div>

      

      {/* Charts */}
      {/* <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Quarterly Budget Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${value}`, 'Amount']} />
                <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card> */}

        {/* <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Resource Allocation</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle>Progress Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={lineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Progress']} />
              <Line 
                type="monotone" 
                dataKey="progress" 
                stroke="#8B5CF6" 
                strokeWidth={3}
                dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card> */}
    </div>
  );
};

export default StatisticsDisplay;
