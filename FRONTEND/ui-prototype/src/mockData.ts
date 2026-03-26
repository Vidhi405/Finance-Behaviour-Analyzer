export const mockUser = {
  name: "Sarah Jenkins",
  avatar: "https://i.pravatar.cc/150?img=32",
  healthScore: 82,
  cluster: "Balanced Spender",
  clusterEmoji: "🔵",
  clusterDescription: "You maintain a healthy balance between saving and spending, though occasional discretionary spikes are noted.",
};

export const mockKPIs = {
  totalSpending: 4250.75,
  spendingTrend: 5.2, // percentage down or up
  avgTransaction: 64.20,
  anomalyCount: 3,
  topCategory: "Food & Dining",
};

export const mockTimeSeriesData = [
  { date: '01 Mar', amount: 120, anomaly: false },
  { date: '05 Mar', amount: 350, anomaly: false },
  { date: '10 Mar', amount: 80, anomaly: false },
  { date: '15 Mar', amount: 1400, anomaly: true }, // Rent + Anomaly spike
  { date: '20 Mar', amount: 200, anomaly: false },
  { date: '25 Mar', amount: 500, anomaly: true }, // Unusually high dining
  { date: '30 Mar', amount: 180, anomaly: false },
];

export const mockCategoryData = [
  { name: 'Housing', value: 1500, color: '#4F8EF7' },
  { name: 'Food & Dining', value: 850, color: '#22C55E' },
  { name: 'Transportation', value: 420, color: '#F59E0B' },
  { name: 'Entertainment', value: 650, color: '#8B5CF6' },
  { name: 'Shopping', value: 450, color: '#EC4899' },
  { name: 'Utilities', value: 380, color: '#06B6D4' },
];

export const mockAnomalies = [
  { id: '1', date: '2026-03-15', category: 'Shopping', amount: 1400, risk: 'High', notes: 'Unusual spike in electronics', reviewed: false },
  { id: '2', date: '2026-03-25', category: 'Food & Dining', amount: 500, risk: 'Medium', notes: 'Large restaurant bill', reviewed: true },
  { id: '3', date: '2026-03-28', category: 'Entertainment', amount: 250, risk: 'Low', notes: 'Multiple weekend tickets', reviewed: false },
];

export const mockInsights = [
  {
    type: 'trend',
    icon: 'TrendingUp',
    title: 'Weekend spending increased',
    message: 'You spent 25% more on weekends compared to last month. Consider moving some discretionary budget to weekdays.',
    action: 'Review Weekend Spent'
  },
  {
    type: 'saving',
    icon: 'PiggyBank',
    title: 'Subscription Savings',
    message: 'You have 3 inactive subscriptions costing $45/month. Canceling them could save you $540 yearly.',
    action: 'Manage Subscriptions'
  },
  {
    type: 'alert',
    icon: 'AlertCircle',
    title: 'Dining out is 40% higher',
    message: 'Your dining expenses are pacing above your typical $600/month average.',
    action: 'Set Dining Limit'
  }
];

export const mockTransactions = [
  { id: 't1', userId: 'U1001', date: '2026-03-30', description: 'Whole Foods Market', category: 'Groceries', amount: 145.20, mode: 'Credit Card', isAnomaly: false },
  { id: 't2', userId: 'U1001', date: '2026-03-28', description: 'AMC Theatres', category: 'Entertainment', amount: 54.00, mode: 'Debit Card', isAnomaly: false },
  { id: 't3', userId: 'U10293', date: '2026-03-25', description: 'Balthazar Restaurant', category: 'Food & Dining', amount: 500.00, mode: 'Credit Card', isAnomaly: true },
  { id: 't4', userId: 'U10293', date: '2026-03-22', description: 'Uber Rides', category: 'Transportation', amount: 24.50, mode: 'Apple Pay', isAnomaly: false },
  { id: 't5', userId: 'U10293', date: '2026-03-15', description: 'Apple Store', category: 'Shopping', amount: 1400.00, mode: 'Credit Card', isAnomaly: true },
  { id: 't6', userId: 'U9999', date: '2026-03-12', description: 'ConEdison', category: 'Utilities', amount: 180.00, mode: 'Bank Transfer', isAnomaly: false },
  { id: 't7', userId: 'U1001', date: '2026-03-10', description: 'Starbucks', category: 'Food & Dining', amount: 6.50, mode: 'Credit Card', isAnomaly: false },
  { id: 't8', userId: 'U9999', date: '2026-03-05', description: 'Target', category: 'Shopping', amount: 112.30, mode: 'Credit Card', isAnomaly: false },
  { id: 't9', userId: 'U1001', date: '2026-03-01', description: 'Rent Payment', category: 'Housing', amount: 1500.00, mode: 'Bank Transfer', isAnomaly: false },
];
