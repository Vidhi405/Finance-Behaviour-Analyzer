import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { useAppContext } from '../../context/AppContext';
import './SpendingAnalytics.css';

export const SpendingAnalytics: React.FC = () => {
  const { transactions } = useAppContext();
  const [timeView, setTimeView] = useState('Weekly');

  // Dynamically generate Time Series Data from transactions
  const timeSeriesMap = transactions.reduce((acc, t) => {
    // Format date string for shorter display "MM-DD"
    const dateParts = t.date.split('-');
    const shortDate = dateParts.length >= 3 ? `${dateParts[1]}-${dateParts[2]}` : t.date;
    
    if (!acc[shortDate]) acc[shortDate] = { date: shortDate, amount: 0, anomaly: false };
    acc[shortDate].amount += t.amount;
    if (t.isAnomaly) acc[shortDate].anomaly = true;
    return acc;
  }, {} as Record<string, any>);
  const dynamicTimeSeriesData = Object.values(timeSeriesMap).sort((a, b) => a.date.localeCompare(b.date));

  // Dynamically generate Category Breakdown Data from transactions
  const categoryMap = transactions.reduce((acc, t) => {
    if (!acc[t.category]) acc[t.category] = { name: t.category, value: 0, color: '' };
    acc[t.category].value += t.amount;
    return acc;
  }, {} as Record<string, any>);
  const dynamicCategoryData = Object.values(categoryMap).sort((a, b) => b.value - a.value);
  
  // Assign predefined colors
  const categoryColors = ['#4F8EF7', '#22C55E', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4'];
  dynamicCategoryData.forEach((item, idx) => {
    item.color = categoryColors[idx % categoryColors.length];
  });

  const CustomTooltipTimeSeries = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{label}</p>
          <p className="tooltip-value">₹{payload[0].value}</p>
          {data.anomaly && <span className="tooltip-alert">High spending</span>}
        </div>
      );
    }
    return null;
  };

  const CustomTooltipCategory = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{payload[0].payload.name}</p>
          <p className="tooltip-value">₹{payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="analytics-container animate-fade-in">
      <div className="analytics-header">
        <h2 className="section-title">Spending Analytics</h2>
      </div>

      <div className="charts-grid">
        <Card className="chart-card time-series">
          <CardHeader>
            <div className="card-header-flex">
              <CardTitle>Time Series Comparison</CardTitle>
              <div className="view-toggle">
                {['Daily', 'Weekly', 'Monthly'].map(view => (
                  <button 
                    key={view}
                    className={`toggle-btn-small ${timeView === view ? 'active' : ''}`}
                    onClick={() => setTimeView(view)}
                  >
                    {view}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="chart-content">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={dynamicTimeSeriesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} />
                <Tooltip content={<CustomTooltipTimeSeries />} />
                <Area 
                  type="monotone" 
                  dataKey="amount" 
                  stroke="var(--color-primary)" 
                  fillOpacity={1} 
                  fill="url(#colorAmount)" 
                  strokeWidth={3}
                  activeDot={{ r: 6, fill: 'var(--color-primary)', stroke: 'white', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="chart-card category-breakdown">
          <CardHeader>
            <CardTitle>Category Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="chart-content">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dynamicCategoryData} layout="vertical" margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--color-border)" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-primary)' }} width={100} />
                <Tooltip cursor={{fill: 'transparent'}} content={<CustomTooltipCategory />} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                  {dynamicCategoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
