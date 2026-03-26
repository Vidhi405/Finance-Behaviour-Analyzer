import React, { useState, useEffect } from 'react';
import { Download, FileText } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { ApiService } from '../../services/api';

export const InsightsReport: React.FC = () => {
  const [reportData, setReportData] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      setIsLoading(true);
      try {
        const data = await ApiService.getInsights();
        // Assume API returns { text: "The insights format string..." } or plain text
        setReportData(data.text || data);
      } catch (err) {
        setReportData("Failed to load insights_report.txt from backend logic. Ensure GET /insights is returning valid text output.");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchReport();
  }, []);

  return (
    <div className="animate-fade-in flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Insights Report</h2>
          <p className="text-secondary text-sm">Comprehensive textual export of the ML model findings.</p>
        </div>
        <Button variant="primary" icon={<Download size={16} />}>Download Text</Button>
      </div>

      <Card>
        <CardContent className="p-8">
          {isLoading ? (
             <div className="flex flex-col gap-4 animate-pulse">
               <div className="h-4 bg-bg rounded w-3/4"></div>
               <div className="h-4 bg-bg rounded w-full"></div>
               <div className="h-4 bg-bg rounded w-5/6"></div>
               <div className="h-4 bg-bg rounded w-2/3"></div>
               <div className="h-4 bg-bg rounded w-4/5 mt-4"></div>
             </div>
          ) : (
             <div className="font-mono text-sm leading-relaxed whitespace-pre-wrap text-text-primary">
               {reportData}
             </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
