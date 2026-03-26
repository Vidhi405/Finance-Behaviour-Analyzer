import React, { useState, useRef } from 'react';
import { Upload, AlertCircle, DollarSign, Users, Activity, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { useAppContext } from '../../context/AppContext';
import { LineChart, Line, BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import toast from 'react-hot-toast';
import './DashboardOverview.css';

export const DashboardOverview: React.FC = () => {
  const { user, kpis, transactions } = useAppContext();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [expandedChart, setExpandedChart] = useState<string | null>('spending');

  if (!user || !kpis) return null;

  // 1. Dynamic Spending Trend (last 7 transaction dates)
  const timeSeriesMap = transactions.reduce((acc, t) => {
    const dateParts = t.date.split('-');
    const shortDate = dateParts.length >= 3 ? `${dateParts[1]}-${dateParts[2]}` : t.date;
    if (!acc[shortDate]) acc[shortDate] = { date: shortDate, amount: 0 };
    acc[shortDate].amount += t.amount;
    return acc;
  }, {} as Record<string, { date: string, amount: number }>);
  const dynamicTimeSeries = Object.values(timeSeriesMap)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-7);

  // 2. Dynamic Top Categories
  const categoryMap = transactions.reduce((acc, t) => {
    if (!acc[t.category]) acc[t.category] = { name: t.category, value: 0 };
    acc[t.category].value += t.amount;
    return acc;
  }, {} as Record<string, { name: string, value: number }>);
  const dynamicCategories = Object.values(categoryMap)
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);

  // 3. Dynamic Weekly Pattern  
  const weeklyMap: Record<string, { day: string, total: number, count: number, avg: number }> = {
    'Sun': { day: 'Sun', total: 0, count: 0, avg: 0 },
    'Mon': { day: 'Mon', total: 0, count: 0, avg: 0 },
    'Tue': { day: 'Tue', total: 0, count: 0, avg: 0 },
    'Wed': { day: 'Wed', total: 0, count: 0, avg: 0 },
    'Thu': { day: 'Thu', total: 0, count: 0, avg: 0 },
    'Fri': { day: 'Fri', total: 0, count: 0, avg: 0 },
    'Sat': { day: 'Sat', total: 0, count: 0, avg: 0 },
  };
  
  transactions.forEach(t => {
     const dateObj = new Date(t.date);
     if (!isNaN(dateObj.getTime())) {
         const dayName = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][dateObj.getDay()];
         weeklyMap[dayName].total += t.amount;
         weeklyMap[dayName].count += 1;
     }
  });
  
  Object.values(weeklyMap).forEach(v => {
      v.avg = v.count > 0 ? parseFloat((v.total / v.count).toFixed(2)) : 0;
  });
  
  const dynamicWeeklyPattern = Object.values(weeklyMap);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a valid CSV file.');
      return;
    }

    setIsUploading(true);
    // Simulate upload -> ML processing phase
    setTimeout(() => {
      toast.success('CSV Uploaded! Backend is analyzing data.');
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }, 1500);
  };

  return (
    <div className="dashboard-overview animate-fade-in flex flex-col gap-6">
      
      {/* Header Section */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Finance Behavior Analyzer</h2>
          <p className="text-secondary text-sm">Real-time ML insights of your transaction data.</p>
        </div>
        
        <div>
          <input 
            type="file" 
            accept=".csv" 
            ref={fileInputRef} 
            onChange={handleFileUpload}
            style={{ display: 'none' }} 
          />
          <Button 
            variant="primary" 
            icon={<Upload size={16} />} 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload CSV'}
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <section className="kpi-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-xs font-semibold text-secondary uppercase tracking-wider mb-1">Total Spend</p>
              <h2 className="text-2xl font-bold">₹{kpis.totalSpending.toLocaleString()}</h2>
            </div>
            <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center text-primary-dark">
              <DollarSign size={24} />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-xs font-semibold text-secondary uppercase tracking-wider mb-1">Avg Transaction</p>
              <h2 className="text-2xl font-bold">₹{kpis.avgTransaction.toFixed(2)}</h2>
            </div>
            <div className="w-12 h-12 rounded-full bg-border flex items-center justify-center text-secondary">
              <Activity size={24} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <p className="text-xs font-semibold text-secondary uppercase tracking-wider">Anomalies</p>
                {kpis.anomalyCount > 0 && <Badge variant="alert">Alert</Badge>}
              </div>
              <h2 className="text-2xl font-bold text-alert">{kpis.anomalyCount}</h2>
            </div>
            <div className="w-12 h-12 rounded-full bg-alert-light flex items-center justify-center text-alert">
              <AlertCircle size={24} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-xs font-semibold text-secondary uppercase tracking-wider mb-1">User Clusters</p>
              <h2 className="text-2xl font-bold">4 Categories</h2>
            </div>
            <div className="w-12 h-12 rounded-full bg-success-light flex items-center justify-center text-success">
              <Users size={24} />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Dynamic Accordion Charts Section */}
      <div className="flex flex-col gap-4">
        
        {/* Accordion 1: Spending Trend */}
        <Card className="overflow-hidden transition-all duration-300">
          <div 
            className="p-6 font-bold text-[1.1rem] flex justify-between items-center cursor-pointer hover:bg-bg/50 transition-colors select-none"
            onClick={() => setExpandedChart(expandedChart === 'spending' ? null : 'spending')}
          >
            <span className="text-text-primary">Spending Trend (7-Day Moving Avg)</span>
            <div className="text-secondary opacity-70">
              {expandedChart === 'spending' ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
            </div>
          </div>
          {expandedChart === 'spending' && (
            <div className="p-6 h-[350px] border-t border-border animate-fade-in">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dynamicTimeSeries} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
                  <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} dy={10} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} tickFormatter={(val) => `₹${val/1000}k`} dx={-10} />
                  <Tooltip 
                    formatter={(value) => [`₹${value}`, 'Amount']}
                    contentStyle={{ backgroundColor: 'var(--color-card)', border: '1px solid var(--color-border)', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  />
                  <Line type="monotone" dataKey="amount" stroke="var(--color-primary)" strokeWidth={3} dot={{ strokeWidth: 2, r: 4, fill: '#fff' }} activeDot={{ r: 6, fill: 'var(--color-primary)' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        {/* Accordion 2: Top Categories */}
        <Card className="overflow-hidden transition-all duration-300">
          <div 
            className="p-6 font-bold text-[1.1rem] flex justify-between items-center cursor-pointer hover:bg-bg/50 transition-colors select-none"
            onClick={() => setExpandedChart(expandedChart === 'categories' ? null : 'categories')}
          >
            <span className="text-text-primary">Top Categories</span>
            <div className="text-secondary opacity-70">
              {expandedChart === 'categories' ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
            </div>
          </div>
          {expandedChart === 'categories' && (
            <div className="p-6 h-[350px] border-t border-border animate-fade-in">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dynamicCategories} layout="vertical" margin={{ top: 10, right: 30, left: 30, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--color-border)" />
                  <XAxis type="number" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} tickFormatter={(val) => `₹${val}`} />
                  <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-primary)' }} width={100} />
                  <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px' }} formatter={(val) => [`₹${val}`, 'Amount']} />
                  <Bar dataKey="value" fill="var(--color-primary)" radius={[0, 4, 4, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        {/* Accordion 3: Weekly Pattern */}
        <Card className="overflow-hidden transition-all duration-300">
          <div 
            className="p-6 font-bold text-[1.1rem] flex justify-between items-center cursor-pointer hover:bg-bg/50 transition-colors select-none"
            onClick={() => setExpandedChart(expandedChart === 'weekly' ? null : 'weekly')}
          >
            <span className="text-text-primary">Weekly Pattern</span>
            <div className="text-secondary opacity-70">
              {expandedChart === 'weekly' ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
            </div>
          </div>
          {expandedChart === 'weekly' && (
            <div className="p-6 h-[350px] border-t border-border animate-fade-in">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dynamicWeeklyPattern} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
                  <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} dy={10} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: 'var(--color-text-secondary)' }} tickFormatter={(val) => `₹${val/1000}k`} />
                  <Tooltip cursor={{ fill: 'var(--color-bg)' }} contentStyle={{ borderRadius: '8px' }} formatter={(val) => [`₹${val}`, 'Average Spent']} />
                  <Bar dataKey="avg" fill="var(--color-success)" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

      </div>

      {/* Anomalies List */}
      <Card>
        <CardContent className="p-0">
          <div className="p-6 border-b border-border flex items-center justify-between">
            <h3 className="text-lg font-bold">Top Anomaly Categories</h3>
            <Badge variant="alert">Requires Attention</Badge>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-bg text-secondary text-xs uppercase tracking-wider">
                  <th className="p-4 font-semibold">Category</th>
                  <th className="p-4 font-semibold">Total Flagged</th>
                  <th className="p-4 font-semibold">Risk Level</th>
                  <th className="p-4 font-semibold">Primary Reason</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr className="border-b border-border hover:bg-bg/50 transition-colors">
                  <td className="p-4 font-medium">Out of Town Spend</td>
                  <td className="p-4 text-alert font-bold">24</td>
                  <td className="p-4"><Badge variant="alert" className="bg-alert-light text-alert">High</Badge></td>
                  <td className="p-4 text-secondary">Geographic location mismatch</td>
                </tr>
                <tr className="border-b border-border hover:bg-bg/50 transition-colors">
                  <td className="p-4 font-medium">Unusual Time</td>
                  <td className="p-4 text-warning font-bold">18</td>
                  <td className="p-4"><Badge variant="warning" className="bg-warning-light text-warning">Medium</Badge></td>
                  <td className="p-4 text-secondary">Transactions between 2AM-5AM</td>
                </tr>
                <tr className="border-b border-border hover:bg-bg/50 transition-colors">
                  <td className="p-4 font-medium">Amount Spike</td>
                  <td className="p-4 text-alert font-bold">12</td>
                  <td className="p-4"><Badge variant="alert" className="bg-alert-light text-alert">High</Badge></td>
                  <td className="p-4 text-secondary">+300% standard deviation</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
