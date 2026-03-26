import React, { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { ChatbotPanel } from './components/layout/ChatbotPanel';
import { DashboardOverview } from './components/dashboard/DashboardOverview';
import { SpendingAnalytics } from './components/analytics/SpendingAnalytics';
import { AnomalyPanel } from './components/anomalies/AnomalyPanel';
import { BehavioralPatterns } from './components/behavior/BehavioralPatterns';
import { AIInsights } from './components/insights/AIInsights';
import { TransactionTable } from './components/transactions/TransactionTable';
import { ReportsView } from './components/reports/ReportsView';
import { UserProfile } from './components/profile/UserProfile';
import { PredictionPage } from './components/prediction/PredictionPage';
import { VisualizationsGallery } from './components/visualizations/VisualizationsGallery';
import { InsightsReport } from './components/insights/InsightsReport';
import { AppProvider, useAppContext } from './context/AppContext';
import { Toaster } from 'react-hot-toast';
import './App.css';

const MainContent: React.FC = () => {
  const { activeTab, isSidebarCollapsed, isLoading } = useAppContext();
  const [isChatOpen, setIsChatOpen] = useState(false);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard': return <DashboardOverview />;
      case 'analytics': return <SpendingAnalytics />;
      case 'anomalies': return <AnomalyPanel />;
      case 'behavior': return <BehavioralPatterns />;
      case 'insights': return <AIInsights />;
      case 'transactions': return <TransactionTable />;
      case 'reports': return <ReportsView />;
      case 'profile': return <UserProfile />;
      case 'prediction': return <PredictionPage />;
      case 'visualizations': return <VisualizationsGallery />;
      case 'insights_report': return <InsightsReport />;
      default:
        return (
          <div className="flex flex-col items-center justify-center h-full text-secondary">
            <h2>Under Construction</h2>
            <p>This module is coming soon.</p>
          </div>
        );
    }
  };

  return (
    <div className="app-container">
      <Sidebar />
      
      <div className={`main-content ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Header onOpenChat={() => setIsChatOpen(true)} />
        
        <main className="page-content">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-full w-full gap-4 text-secondary">
               <div className="animate-pulse">Loading ML Models & Financial Data...</div>
            </div>
          ) : (
            renderActiveTab()
          )}
        </main>
      </div>

      <ChatbotPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--color-card)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-lg)'
          }
        }}
      />
      <MainContent />
    </AppProvider>
  );
};

export default App;
