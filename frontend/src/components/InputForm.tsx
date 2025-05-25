
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { FormData } from './DataAnalysisApp';
import { MapPin, DollarSign, Palette } from 'lucide-react';
import LocationPicker from './LocationPicker'

interface InputFormProps {
  onExecute: (data: FormData) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onExecute }) => {
  const [theme, setTheme] = useState('');
  const [budget, setBudget] = useState<number>(0);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const formData = new FormData()
    if (location) {
      formData.append('latitude', location.lat.toString())
      formData.append('longitude', location.lng.toString())
    }


    
    if (!location || !theme || budget <= 0 ) {
      alert('Please fill in all fields');
      return;
    }

    onExecute({
      location,
      theme,
      budget
    });
  };

  return (
    <Card className="max-w-2xl mx-auto shadow-lg border-0 bg-white/80 backdrop-blur-sm">
      <CardHeader className="text-center bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
        <CardTitle className="text-2xl font-bold">Analysis Parameters</CardTitle>
      </CardHeader>
      <CardContent className="p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="location" className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Location
            </Label>
            <LocationPicker onLocationSelect={setLocation} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="theme" className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Theme
            </Label>
            <Input
              id="theme"
              type="text"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="Enter theme (e.g., Technology, Healthcare, Education)"
              className="transition-all duration-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="budget" className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Budget
            </Label>
            <Input
              id="budget"
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              placeholder="Enter budget amount"
              min="1"
              className="transition-all duration-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
          >
            Execute Analysis
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default InputForm;
