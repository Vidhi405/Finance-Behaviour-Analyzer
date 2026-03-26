import React from 'react';
import { Download, FileText, Calendar, Filter } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import './ReportsView.css';

const mockReports = [
  { id: 1, title: 'March 2026 Monthly Summary', type: 'Monthly', date: '2026-03-31', size: '2.4 MB', status: 'Ready' },
  { id: 2, title: 'Q1 2026 Expense Breakdown', type: 'Quarterly', date: '2026-03-31', size: '5.1 MB', status: 'Processing' },
  { id: 3, title: 'February 2026 Monthly Summary', type: 'Monthly', date: '2026-02-28', size: '2.2 MB', status: 'Ready' },
  { id: 4, title: '2025 Annual Tax Report', type: 'Tax', date: '2026-01-15', size: '8.7 MB', status: 'Ready' },
  { id: 5, title: 'Behavioral Cluster Analysis', type: 'Insight', date: '2026-03-10', size: '1.5 MB', status: 'Ready' },
];

export const ReportsView: React.FC = () => {
  return (
    <div className="reports-container animate-fade-in">
      <div className="section-header reports-header">
        <div>
          <h2 className="section-title">Reports & Exports</h2>
          <p className="section-subtitle text-secondary">Download statements and analytical summaries.</p>
        </div>
        <Button variant="primary" icon={<FileText size={16} />}>Generate New Report</Button>
      </div>

      <div className="reports-filters">
        <Button variant="secondary" size="sm" icon={<Calendar size={14} />}>Date Range</Button>
        <Button variant="secondary" size="sm" icon={<Filter size={14} />}>Report Type</Button>
      </div>

      <div className="reports-grid">
        {mockReports.map(report => (
          <Card key={report.id} className="report-card">
            <CardContent className="report-content">
              <div className="report-icon bg-primary-light text-primary">
                <FileText size={24} />
              </div>
              <div className="report-info">
                <h3 className="report-title">{report.title}</h3>
                <div className="report-meta text-secondary">
                  <span>{report.date}</span>
                  <span>•</span>
                  <span>{report.size}</span>
                </div>
              </div>
              <div className="report-actions">
                <Badge variant={report.status === 'Ready' ? 'success' : 'warning'}>
                  {report.status}
                </Badge>
                {report.status === 'Ready' && (
                  <Button variant="ghost" size="sm" className="download-btn">
                    <Download size={18} />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
