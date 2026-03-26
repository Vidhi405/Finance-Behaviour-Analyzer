import React, { useState } from 'react';
import { X, Send, Bot, User, CornerDownLeft } from 'lucide-react';
import { Button } from '../ui/Button';
import './ChatbotPanel.css';

interface ChatbotPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatbotPanel: React.FC<ChatbotPanelProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', text: 'Hello! I am FinScan AI. Ask me anything about your spending, anomalies, or savings opportunities.' }
  ]);

  const handleSend = () => {
    if (!query.trim()) return;
    
    // Add user message
    const newMsg = { id: Date.now(), type: 'user', text: query };
    setMessages(prev => [...prev, newMsg]);
    setQuery('');

    // Simulate AI response
    setTimeout(() => {
      let botResponse = 'I observed that your recent spending on dining is 40% higher than your average. Consider reducing weekend restaurant visits to stay within budget.';
      if (query.toLowerCase().includes('anomaly')) {
        botResponse = 'You have 3 flagged anomalies this month. The highest is a $1,400 transaction at Apple Store on Mar 15. Would you like me to mark it as expected?';
      }
      setMessages(prev => [...prev, { id: Date.now() + 1, type: 'bot', text: botResponse }]);
    }, 1000);
  };

  if (!isOpen) return null;

  return (
    <div className="chatbot-overlay" onClick={onClose}>
      <div className="chatbot-panel" onClick={e => e.stopPropagation()}>
        <div className="chatbot-header">
          <div className="chatbot-title">
            <Bot size={20} className="text-primary" />
            <h3>FinScan Assistant</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="chatbot-messages">
          {messages.map(msg => (
            <div key={msg.id} className={`chat-message ${msg.type}`}>
              <div className="msg-avatar">
                {msg.type === 'bot' ? <Bot size={16} /> : <User size={16} />}
              </div>
              <div className="msg-bubble">
                <p>{msg.text}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="chatbot-input">
          <input 
            type="text" 
            value={query} 
            onChange={e => setQuery(e.target.value)}
            placeholder="Ask about your finances..."
            onKeyDown={e => e.key === 'Enter' && handleSend()}
          />
          <Button 
            variant="primary" 
            size="sm" 
            onClick={handleSend}
            disabled={!query.trim()}
            className="send-btn"
          >
            <Send size={16} />
          </Button>
        </div>
      </div>
    </div>
  );
};
