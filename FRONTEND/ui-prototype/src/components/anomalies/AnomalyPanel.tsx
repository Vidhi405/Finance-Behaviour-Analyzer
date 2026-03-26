import React, { useState } from 'react';
import { AlertOctagon, CheckCircle2, AlertTriangle, Flag, ShieldAlert } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { useAppContext } from '../../context/AppContext';
import './AnomalyPanel.css';

export const AnomalyPanel: React.FC = () => {
  const { transactions } = useAppContext();
  const [reviewedMap, setReviewedMap] = useState<Record<string, boolean>>({});

  // Dynamically derive anomalies from the master transactions array
  const dynamicAnomalies = transactions
    .filter(t => t.isAnomaly)
    .map(t => ({
      id: t.id,
      date: t.date,
      category: t.category,
      amount: t.amount,
      risk: t.amount > 1000 ? 'High' : (t.amount > 400 ? 'Medium' : 'Low'),
      notes: t.description || 'System flagged anomalous pattern',
      reviewed: !!reviewedMap[t.id]
    }));

  const toggleReviewed = (id: string) => {
    setReviewedMap(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const totalAmount = dynamicAnomalies.reduce((sum, a) => sum + a.amount, 0);
  const unreviewedCount = dynamicAnomalies.filter(a => !a.reviewed).length;
  
  // Overall risk based on highest unreviewed anomaly
  const hasHighRisk = dynamicAnomalies.some(a => a.risk === 'High' && !a.reviewed);
  const hasMediumRisk = dynamicAnomalies.some(a => a.risk === 'Medium' && !a.reviewed);
  const overallRisk = hasHighRisk ? 'High' : hasMediumRisk ? 'Medium' : 'Low';

  return (
    <div className="anomaly-container animate-fade-in">
      <div className="section-header">
        <h2 className="section-title">Anomaly Detection</h2>
        <p className="section-subtitle text-secondary">AI-driven detection of unusual spending patterns and duplicate charges.</p>
      </div>

      <div className="risk-summary-grid">
        <Card className="summary-card">
          <CardContent className="summary-content">
            <div className="summary-icon-wrapper bg-alert-light text-alert">
              <ShieldAlert size={24} />
            </div>
            <div className="summary-info">
              <p className="summary-label">Total Anomalies</p>
              <h2 className="summary-value">{dynamicAnomalies.length}</h2>
            </div>
          </CardContent>
        </Card>

        <Card className="summary-card">
          <CardContent className="summary-content">
            <div className="summary-icon-wrapper bg-warning-light text-warning">
              <AlertOctagon size={24} />
            </div>
            <div className="summary-info">
              <p className="summary-label">Total Value at Risk</p>
              <h2 className="summary-value">₹{totalAmount.toLocaleString()}</h2>
            </div>
          </CardContent>
        </Card>

        <Card className={`summary-card risk-level-${overallRisk.toLowerCase()}`}>
          <CardContent className="summary-content">
            <div className="summary-icon-wrapper">
              {overallRisk === 'High' ? <AlertTriangle size={24} /> : <CheckCircle2 size={24} />}
            </div>
            <div className="summary-info">
              <p className="summary-label">Current Risk Level</p>
              <h2 className="summary-value">{overallRisk} Risk</h2>
              <span className="risk-subtitle">({unreviewedCount} unreviewed)</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="anomaly-table-card">
        <div className="table-wrapper">
          <table className="custom-table">
            <thead>
              <tr>
                <th style={{ width: '50px' }}>Review</th>
                <th>Date</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Risk Level</th>
                <th>Notes</th>
                <th align="right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {dynamicAnomalies.map((anomaly) => (
                <tr key={anomaly.id} className={`table-row ${anomaly.risk.toLowerCase()}-risk ${anomaly.reviewed ? 'is-reviewed' : ''}`}>
                  <td className="checkbox-cell">
                    <input 
                      type="checkbox" 
                      className="custom-checkbox"
                      checked={anomaly.reviewed}
                      onChange={() => toggleReviewed(anomaly.id)}
                    />
                  </td>
                  <td>{anomaly.date}</td>
                  <td className="font-medium">{anomaly.category}</td>
                  <td className="amount-cell">₹{anomaly.amount.toFixed(2)}</td>
                  <td>
                    <Badge variant={
                      anomaly.risk === 'High' ? 'alert' : 
                      anomaly.risk === 'Medium' ? 'warning' : 'success'
                    }>
                      {anomaly.risk}
                    </Badge>
                  </td>
                  <td className="text-secondary text-sm">{anomaly.notes}</td>
                  <td align="right">
                    <Button variant="ghost" size="sm" icon={<Flag size={14} className="text-secondary" />}>
                      Report
                    </Button>
                  </td>
                </tr>
              ))}
              {dynamicAnomalies.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-state">No anomalies detected. You're all good!</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
