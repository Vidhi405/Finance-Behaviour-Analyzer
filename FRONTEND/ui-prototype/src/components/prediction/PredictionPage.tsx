import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, User, Calendar, IndianRupee, Tag, CreditCard, Activity } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { ApiService } from '../../services/api';
import type { PredictFormValues, PredictionResult } from '../../services/api';
import { useAppContext } from '../../context/AppContext';
import toast from 'react-hot-toast';

export const PredictionPage: React.FC = () => {
  const { setTransactions } = useAppContext();
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [formData, setFormData] = useState<PredictFormValues>({
    amount: 0,
    category: '',
    paymentMode: '',
    date: new Date().toISOString().split('T')[0],
    userId: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.amount || !formData.category || !formData.paymentMode || !formData.userId) {
      toast.error('Please fill all required fields');
      return;
    }

    setIsPredicting(true);
    setResult(null);
    try {
      const prediction = await ApiService.predictTransaction(formData);
      setResult(prediction);
      
      // Inject the newly predicted transaction straight into global context
      // so that it immediately dynamically reflects on the Spending Analytics graphs.
      setTransactions(prev => [{
        id: `p-${Date.now()}`,
        userId: formData.userId,
        date: formData.date,
        description: 'Simulated User Input',
        category: formData.category,
        amount: formData.amount,
        mode: formData.paymentMode,
        isAnomaly: prediction.isAnomaly
      }, ...prev]);
      
      toast.success('Prediction generated & added to datasets');
    } catch {
      // toast handled in api layer
    } finally {
      setIsPredicting(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Low': return 'var(--color-success)';
      case 'Medium': return 'var(--color-warning)';
      case 'High': return 'var(--color-alert)';
      default: return 'var(--color-text-secondary)';
    }
  };

  return (
    <div className="animate-fade-in flex flex-col gap-8" style={{ maxWidth: '750px', margin: '0 auto', padding: '20px 0' }}>
      <div className="text-center mb-2">
        <div className="inline-flex items-center justify-center p-4 bg-primary/10 rounded-full mb-4 text-primary">
          <Activity size={32} />
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-text-primary mb-2">Transaction Prediction</h2>
        <p className="text-secondary text-sm max-w-lg mx-auto leading-relaxed">Simulate a real-time transaction against the core ML model to detect anomalies and classify behavior clusters.</p>
      </div>

      <Card className="shadow-md border-0 ring-1 ring-border">
        <CardContent className="p-8">
          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-bold text-secondary uppercase tracking-wider">User ID</label>
                <div className="relative">
                  <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-secondary" />
                  <input 
                    type="text" 
                    value={formData.userId}
                    onChange={(e) => setFormData({...formData, userId: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-bg focus:bg-white text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all placeholder:text-text-secondary/50 font-medium text-text-primary" 
                    placeholder="e.g. U10293"
                  />
                </div>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-bold text-secondary uppercase tracking-wider">Date</label>
                <div className="relative">
                  <Calendar size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-secondary" />
                  <input 
                    type="date" 
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-bg focus:bg-white text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all font-medium text-text-primary" 
                  />
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] font-bold text-secondary uppercase tracking-wider">Amount (₹)</label>
              <div className="relative">
                <IndianRupee size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-secondary" />
                <input 
                  type="number" 
                  value={formData.amount}
                  onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
                  className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-bg focus:bg-white text-lg font-bold outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all placeholder:text-text-secondary/30 text-text-primary" 
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-bold text-secondary uppercase tracking-wider">Category</label>
                <div className="relative">
                  <Tag size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-secondary z-10" />
                  <select 
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-bg focus:bg-white text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all appearance-none font-medium text-text-primary"
                  >
                    <option value="" className="text-secondary">Select Category...</option>
                    <option value="Food">Food & Dining</option>
                    <option value="Travel">Travel & Transportation</option>
                    <option value="Shopping">Shopping</option>
                    <option value="Bills">Bills & Utilities</option>
                    <option value="Entertainment">Entertainment</option>
                    <option value="Housing">Housing</option>
                  </select>
                </div>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] font-bold text-secondary uppercase tracking-wider">Payment Mode</label>
                <div className="relative">
                  <CreditCard size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-secondary z-10" />
                  <select 
                    value={formData.paymentMode}
                    onChange={(e) => setFormData({...formData, paymentMode: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-bg focus:bg-white text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all appearance-none font-medium text-text-primary"
                  >
                    <option value="" className="text-secondary">Select Method...</option>
                    <option value="UPI">UPI</option>
                    <option value="Credit Card">Credit Card</option>
                    <option value="Debit Card">Debit Card</option>
                    <option value="Net Banking">Net Banking</option>
                    <option value="Wallet">Digital Wallet</option>
                    <option value="Apple Pay">Apple Pay</option>
                    <option value="Cash">Cash</option>
                  </select>
                </div>
              </div>
            </div>

            <Button variant="primary" type="submit" className="mt-6 py-3.5 text-sm font-bold flex justify-center w-full shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-shadow" disabled={isPredicting}>
              {isPredicting ? 'Evaluating Model...' : 'Run Prediction'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card className={`animate-slide-up border-2 ${result.isAnomaly ? 'border-alert' : 'border-success'}`}>
          <CardContent className="p-6 flex flex-col gap-4">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                {result.isAnomaly ? <ShieldAlert size={32} className="text-alert" /> : <CheckCircle size={32} className="text-success" />}
                <div>
                  <h3 className="font-bold text-lg" style={{ color: result.isAnomaly ? 'var(--color-alert)' : 'var(--color-success)' }}>
                    {result.isAnomaly ? 'Anomaly Detected' : 'Normal Transaction'}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs uppercase font-semibold text-secondary">Risk Level:</span>
                    <strong style={{ color: getRiskColor(result.riskLevel) }}>{result.riskLevel}</strong>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <span className="text-xs text-secondary uppercase">Assigned Profile</span>
                <div className="mt-1">
                  <Badge variant="primary" style={{ backgroundColor: `var(--color-cluster-${result.cluster}-bg)`, color: `var(--color-cluster-${result.cluster})` }}>
                    Cluster {result.cluster}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="bg-bg rounded-md p-4 text-sm mt-2 border border-border">
              <span className="font-semibold block mb-1">Model Explanation:</span>
              <span className="text-secondary">{result.explanation}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
