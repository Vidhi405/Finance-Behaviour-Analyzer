import axios from 'axios';
import toast from 'react-hot-toast';

// Base URL for the FastAPI Backend.
// In a true prod environment, use import.meta.env.VITE_API_BASE_URL
const API_BASE_URL = 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 seconds fail-safe timeout
});

// Configure robust error interception
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMsg = error.response?.data?.message || error.message || 'An unexpected error occurred';
    toast.error(`API Error: ${errorMsg}`);
    return Promise.reject(error);
  }
);

// Types
export interface PredictFormValues {
  amount: number;
  category: string;
  paymentMode: string;
  date: string;
  userId: string;
}

export interface PredictionResult {
  isAnomaly: boolean;
  riskLevel: 'Low' | 'Medium' | 'High';
  cluster: number;
  explanation: string;
}

// Service Methods
export const ApiService = {
  getSummary: async () => {
    const response = await apiClient.get('/summary');
    return response.data;
  },
  
  getInsights: async () => {
    const response = await apiClient.get('/insights');
    return response.data;
  },
  
  getUserProfile: async (userId: string) => {
    const response = await apiClient.get(`/user/${userId}`);
    return response.data;
  },
  
  predictTransaction: async (data: PredictFormValues): Promise<PredictionResult> => {
    const response = await apiClient.post('/predict', data);
    return response.data;
  },
  
  getVisualizationsList: async () => {
    const response = await apiClient.get('/visualizations');
    return response.data;
  },
  
  // Helper to construct the full URL for an image src attribute
  getVisualizationImageUrl: (filename: string) => {
    return `${API_BASE_URL}/visualizations/${filename}`;
  },

  checkHealth: async () => {
    const response = await apiClient.get('/');
    return response.data;
  }
};
