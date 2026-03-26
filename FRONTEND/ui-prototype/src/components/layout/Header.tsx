import React, { useState } from 'react';
import { Bell, Mic, Search } from 'lucide-react';
import { useAppContext } from '../../context/AppContext';
import { Badge } from '../ui/Badge';
import './Header.css';

interface HeaderProps {
  onOpenChat: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenChat }) => {
  const { isSidebarCollapsed, isLoading, user } = useAppContext();
  const [isRecording, setIsRecording] = useState(false);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setTimeout(() => onOpenChat(), 1500); // Simulate opening chat after voice command
    }
  };

  return (
    <header className={`app-header ${isSidebarCollapsed ? 'expanded' : ''}`}>
      <div className="header-left">
        <h2 className="greeting">Good morning, {user?.name.split(' ')[0]}</h2>
        {isLoading && <span className="loading-indicator animate-pulse">Syncing data...</span>}
      </div>

      <div className="header-center">
        <div className="search-bar">
          <Search size={18} className="search-icon" />
          <input type="text" placeholder="Search transactions (e.g., 'Starbucks')" />
          <kbd className="shortcut-key">⌘K</kbd>
        </div>
      </div>

      <div className="header-right">
        <button 
          className={`icon-btn mic-btn ${isRecording ? 'recording' : ''}`} 
          onClick={toggleRecording}
          title="Voice command (AI Assistant)"
        >
          <Mic size={20} />
          {isRecording && <span className="ping-dot"></span>}
        </button>

        <button className="icon-btn notif-btn">
          <Bell size={20} />
          <span className="notif-badge">3</span>
        </button>

        <div className="user-profile">
          <img src={user?.avatar} alt={user?.name} className="avatar" />
          <div className="user-info">
            <span className="user-name">{user?.name}</span>
            <Badge variant="primary" className="cluster-badge text-xs">
              {user?.clusterEmoji} {user?.cluster}
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
};
