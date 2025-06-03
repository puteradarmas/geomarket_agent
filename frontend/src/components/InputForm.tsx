
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
  onShowHistory: () => void;
}

const InputForm: React.FC<InputFormProps> = ({ onExecute, onShowHistory }) => {
  const [additional_prompt, setTheme] = useState('');
  const [budget, setBudget] = useState<number>(1);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const formData = new FormData()
    if (location) {
      formData.append('latitude', location.lat.toString())
      formData.append('longitude', location.lng.toString())
    }


    
    if (!additional_prompt || budget <= 0 ) {
      alert('Please fill in all fields');
      return;
    }

    onExecute({
      location,
      additional_prompt,
    });
  };


  return (
    <Card className="max-w-2xl mx-auto shadow-lg border-0 bg-white/80 backdrop-blur-sm">
      <CardHeader className="text-center bg-gradient-to-br from-blue-800 to-purple-700 text-white rounded-t-lg">
        <CardTitle className="text-2xl font-bold">Analysis Parameters</CardTitle>
      </CardHeader>
      <CardContent className="p-8">
        <div className="flex justify-end mt-2">
          <Button onClick={onShowHistory} variant="outline" className="hover:bg-gray-50">
            Show History
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="location" className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Location
            </Label>
            
            <LocationPicker onLocationSelect={setLocation} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="additional_prompt" className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Prompt
            </Label>
            <Input
              id="additional_prompt"
              type="text"
              value={additional_prompt}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="Enter Additional Prompt"
              className="transition-all duration-200 focus:ring-2 focus:ring-blue-500"
            />
          </div>


          <Button
            type="submit"
            className="w-full bg-gradient-to-br from-blue-800/80 to-purple-600/60 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
          >
            Execute Analysis
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default InputForm;
