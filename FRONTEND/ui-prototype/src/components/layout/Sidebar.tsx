import React, { useState, useRef, useEffect } from 'react';
import { Home, PieChart, AlertTriangle, Activity, Zap, FileText, Menu, Settings, User, Sliders, LogOut, Users, FileSearch, Image as ImageIcon } from 'lucide-react';
import { useAppContext } from '../../context/AppContext';
import './Sidebar.css';

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'profile', label: 'User Profile', icon: Users },
  { id: 'prediction', label: 'Transaction Prediction', icon: Activity },
  { id: 'analytics', label: 'Spending Analytics', icon: PieChart },
  { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
  { id: 'behavior', label: 'Behavioral Patterns', icon: Zap },
  { id: 'visualizations', label: 'Visualizations', icon: ImageIcon },
  { id: 'insights_report', label: 'Insights Report', icon: FileSearch },
  { id: 'transactions', label: 'Transactions', icon: FileText },
  { id: 'reports', label: 'Exports', icon: FileText },
];

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, isSidebarCollapsed, setIsSidebarCollapsed } = useAppContext();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
        setIsSettingsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <aside className={`sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!isSidebarCollapsed && <div className="logo-container">
          <div className="logo-icon">
            <Zap size={20} color="white" />
          </div>
          <h1 className="logo-text">FinScan<span className="logo-accent">AI</span></h1>
        </div>}
        <button 
          className="toggle-btn"
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        >
          <Menu size={20} />
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
              title={isSidebarCollapsed ? item.label : undefined}
            >
              <Icon size={20} className="nav-icon" />
              {!isSidebarCollapsed && <span className="nav-label">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer" ref={settingsRef}>
        {isSettingsOpen && (
          <div className="settings-menu">
            <button className="settings-menu-item" onClick={() => setIsSettingsOpen(false)}>
              <User size={16} />
              <span>Profile Settings</span>
            </button>
            <button className="settings-menu-item" onClick={() => setIsSettingsOpen(false)}>
              <Sliders size={16} />
              <span>Preferences</span>
            </button>
            <button className="settings-menu-item danger" onClick={() => setIsSettingsOpen(false)}>
              <LogOut size={16} />
              <span>Log out</span>
            </button>
          </div>
        )}
        <button 
          className={`nav-item ${isSettingsOpen ? 'active' : ''}`}
          onClick={() => setIsSettingsOpen(!isSettingsOpen)}
        >
          <Settings size={20} className="nav-icon" />
          {!isSidebarCollapsed && <span className="nav-label">Settings</span>}
        </button>
      </div>
    </aside>
  );
};
