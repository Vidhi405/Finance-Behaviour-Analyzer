import React from 'react';
import { TrendingUp, PiggyBank, AlertCircle, ArrowRight } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { useAppContext } from '../../context/AppContext';
import './AIInsights.css';

const IconMap: { [key: string]: React.ElementType } = {
  TrendingUp,
  PiggyBank,
  AlertCircle
};

export const AIInsights: React.FC = () => {
  const { insights } = useAppContext();

  return (
    <div className="insights-container animate-fade-in">
      <div className="section-header">
        <h2 className="section-title">AI Insights</h2>
        <p className="section-subtitle text-secondary">Actionable intelligence derived from your transaction history.</p>
      </div>

      <div className="insights-grid">
        {insights.map((insight, index) => {
          const Icon = IconMap[insight.icon];
          const colorClass = 
            insight.type === 'trend' ? 'text-primary' : 
            insight.type === 'saving' ? 'text-success' : 'text-alert';
            
          const bgClass = 
            insight.type === 'trend' ? 'bg-primary-light' : 
            insight.type === 'saving' ? 'bg-success-light' : 'bg-alert-light';

          return (
            <Card key={index} className="insight-card">
              <CardContent className="insight-content">
                <div className={`insight-icon-container ${bgClass} ${colorClass}`}>
                  <Icon size={24} />
                </div>
                
                <h3 className="insight-title">{insight.title}</h3>
                <p className="insight-message text-secondary">{insight.message}</p>
                
                <div className="insight-action">
                  <span className={`insight-action-text ${colorClass}`}>{insight.action}</span>
                  <ArrowRight size={16} className={colorClass} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="savings-opportunity-card mt-6">
        <CardContent className="savings-content">
          <div className="savings-info">
            <PiggyBank size={40} className="text-success" />
            <div>
              <h2 className="savings-title text-success">Estimated Monthly Savings</h2>
              <p className="text-secondary">Based on our cluster optimization algorithm, you could save more.</p>
            </div>
          </div>
          <div className="savings-amount">
            <span>$</span>540<span>/mo</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
