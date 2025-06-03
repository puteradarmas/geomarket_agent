import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { HistData } from './DataAnalysisApp';

type HistoryDisplayProps = {
  HistData: HistData;
  onViewHistory: (id:number) => void;
};


const HistoryDisplay: React.FC<HistoryDisplayProps> = ({HistData,onViewHistory}) => {


  // console.log("Received from Hist Data 1:", HistData);
  // console.log("Type of HistData:", typeof HistData);

  // console.log("HistData content:", HistData);
  // console.log("HistData[0] type:", typeof HistData[0]);
  // console.log("HistData[0] keys:", Object.keys(HistData || {}));

  if (!HistData.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>History</CardTitle>
        </CardHeader>
        <CardContent>No history available.</CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>History</CardTitle>
      </CardHeader>
      <CardContent className="overflow-auto">
        <table className="w-full table-auto text-sm border border-gray-200">
          <thead className="bg-gray-100">
            <tr>
                <th className="text-left px-4 py-2 border-b">ID</th>
                <th className="text-left px-4 py-2 border-b">Latitude</th>
                <th className="text-left px-4 py-2 border-b">Longitude</th>
                <th className="text-left px-4 py-2 border-b">Address</th>
                <th className="text-left px-4 py-2 border-b">Created At</th>
                <th className="text-left px-4 py-2 border-b"></th>
            </tr>
          </thead>
          <tbody>
            {HistData.map((entry) => (
              <tr key={entry.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 border-b">{entry.id}</td>
                <td className="px-4 py-2 border-b">{entry.lat}</td>
                <td className="px-4 py-2 border-b">{entry.lgn}</td>
                <td className="px-4 py-2 border-b">{entry.address}</td>
                <td className="px-4 py-2 border-b">{new Date(entry.created_at).toLocaleString()}</td>
                <td className="px-4 py-2 border-b">
                  <Button
                    variant="outline"
                    onClick={() => onViewHistory(entry.id)}
                  >
                    View
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
};

export default HistoryDisplay;