
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { FormData } from './DataAnalysisApp';
import { Download } from 'lucide-react';

interface DataTableProps {
  formData: FormData;
}

const DataTable: React.FC<DataTableProps> = ({ formData }) => {
  // Generate mock data based on form inputs
  const generateTableData = () => {
    const baseData = [
      { id: 1, metric: 'Cost Efficiency', value: '92%', target: '85%', status: 'Exceeded' },
      { id: 2, metric: 'Timeline Adherence', value: '88%', target: '90%', status: 'Near Target' },
      { id: 3, metric: 'Quality Score', value: '96%', target: '95%', status: 'Exceeded' },
      { id: 4, metric: 'Resource Utilization', value: '84%', target: '80%', status: 'Exceeded' },
      { id: 5, metric: 'Stakeholder Satisfaction', value: '91%', target: '85%', status: 'Exceeded' },
      { id: 6, metric: 'Risk Mitigation', value: '78%', target: '75%', status: 'Exceeded' },
      { id: 7, metric: 'Innovation Index', value: '87%', target: '80%', status: 'Exceeded' },
      { id: 8, metric: 'Sustainability Score', value: '82%', target: '85%', status: 'Below Target' }
    ];

    return baseData.map(item => ({
      ...item,
      location: formData.location,
      theme: formData.theme,
      budget: Math.floor(formData.budget / 8), // Distribute budget across metrics
      category: formData.category,
      priority: formData.priority
    }));
  };

  const tableData = generateTableData();

  const downloadCSV = () => {
    const headers = ['ID', 'Metric', 'Value', 'Target', 'Status', 'Location', 'Theme', 'Budget Allocation', 'Category', 'Priority'];
    const csvContent = [
      headers.join(','),
      ...tableData.map(row => [
        row.id,
        row.metric,
        row.value,
        row.target,
        row.status,
        row.location,
        row.theme,
        row.budget,
        row.category,
        row.priority
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `analysis_results_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Exceeded':
        return 'text-green-600 bg-green-100';
      case 'Near Target':
        return 'text-yellow-600 bg-yellow-100';
      case 'Below Target':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <Card className="shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Detailed Analysis Data</CardTitle>
        <Button
          onClick={downloadCSV}
          className="bg-green-600 hover:bg-green-700 text-white flex items-center gap-2"
        >
          <Download className="h-4 w-4" />
          Download CSV
        </Button>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead>Current Value</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Budget Allocation</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Priority</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.map((row) => (
                <TableRow key={row.id} className="hover:bg-gray-50 transition-colors">
                  <TableCell className="font-medium">{row.metric}</TableCell>
                  <TableCell className="font-semibold text-blue-600">{row.value}</TableCell>
                  <TableCell>{row.target}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(row.status)}`}>
                      {row.status}
                    </span>
                  </TableCell>
                  <TableCell>${row.budget.toLocaleString()}</TableCell>
                  <TableCell className="capitalize">{row.category}</TableCell>
                  <TableCell className="capitalize">{row.priority}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">Analysis Summary</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Location:</span>
              <span className="ml-2 font-medium">{formData.location}</span>
            </div>
            <div>
              <span className="text-gray-600">Theme:</span>
              <span className="ml-2 font-medium">{formData.theme}</span>
            </div>
            <div>
              <span className="text-gray-600">Total Budget:</span>
              <span className="ml-2 font-medium">${formData.budget.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-gray-600">Timeframe:</span>
              <span className="ml-2 font-medium">{formData.timeframe}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DataTable;
