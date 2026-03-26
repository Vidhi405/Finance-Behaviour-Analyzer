import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  mockUser, 
  mockKPIs, 
  mockTimeSeriesData, 
  mockCategoryData, 
  mockAnomalies, 
  mockInsights, 
  mockTransactions 
} from '../mockData';

// Data Types
export type User = typeof mockUser;
export type KPIs = typeof mockKPIs;
export type TimeSeriesData = typeof mockTimeSeriesData;
export type CategoryData = typeof mockCategoryData;
export type Anomaly = typeof mockAnomalies[0];
export type Insight = typeof mockInsights[0];
export type Transaction = typeof mockTransactions[0];

type AppContextType = {
  // UI State
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: (collapsed: boolean) => void;
  dateRange: string;
  setDateRange: (range: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  // Data State
  user: User | null;
  kpis: KPIs | null;
  timeSeriesData: TimeSeriesData;
  categoryData: CategoryData;
  anomalies: Anomaly[];
  setAnomalies: React.Dispatch<React.SetStateAction<Anomaly[]>>;
  insights: Insight[];
  transactions: Transaction[];
  setTransactions: React.Dispatch<React.SetStateAction<Transaction[]>>;
  
  // Actions
  fetchData: () => Promise<void>;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [dateRange, setDateRange] = useState('this-month');
  const [isLoading, setIsLoading] = useState(true);

  // Data State Initializers
  const [user, setUser] = useState<User | null>(null);
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData>([]);
  const [categoryData, setCategoryData] = useState<CategoryData>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      // TODO: REPLACE THIS BLOCK WITH ACTUAL `fetch()` TO YOUR ML BACKEND
      // Example: const res = await fetch('http://localhost:5000/api/dashboard');
      // const data = await res.json();
      
      // Simulating network delay for backend mockup
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock Data Assignment (Replace with data from fetch)
      setUser(mockUser);
      setKpis(mockKPIs);
      setTimeSeriesData(mockTimeSeriesData);
      setCategoryData(mockCategoryData);
      setAnomalies(mockAnomalies);
      setInsights(mockInsights);
      setTransactions(mockTransactions);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        dateRange,
        setDateRange,
        isLoading,
        setIsLoading,
        
        user,
        kpis,
        timeSeriesData,
        categoryData,
        anomalies,
        setAnomalies,
        insights,
        transactions,
        setTransactions,
        
        fetchData
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
