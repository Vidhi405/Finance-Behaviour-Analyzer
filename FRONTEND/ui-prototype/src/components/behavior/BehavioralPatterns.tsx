import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useAppContext } from '../../context/AppContext';
import './BehavioralPatterns.css';
import { Lightbulb } from 'lucide-react';

const clusterData = [
  { name: 'Big Spender', value: 15, color: '#EF4444' }, // Red (Alert)
  { name: 'Balanced Spender', value: 45, color: '#4F8EF7' }, // Blue (Primary)
  { name: 'Occasional Spender', value: 25, color: '#F59E0B' }, // Amber (Warning)
  { name: 'Frugal Spender', value: 15, color: '#22C55E' } // Green (Success)
];

export const BehavioralPatterns: React.FC = () => {
  const { user } = useAppContext();
  
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{payload[0].payload.name}</p>
          <p className="tooltip-value">{payload[0].value}% Users</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="behavior-container animate-fade-in">
      <div className="section-header">
        <h2 className="section-title">Behavioral Patterns</h2>
        <p className="section-subtitle text-secondary">Discover your financial phenotype based on analysis of user cohorts.</p>
      </div>

      <div className="behavior-grid">
        <Card className="profile-card">
          <CardContent className="profile-content">
            <div className="profile-header">
              <div className="profile-avatar-large">
                <img src={user?.avatar} alt="User Avatar" />
                <div className="cluster-emoji-badge">{user?.clusterEmoji}</div>
              </div>
              <div className="profile-details">
                <h3 className="profile-name">{user?.name}</h3>
                <Badge variant="primary">Your Cluster</Badge>
              </div>
            </div>

            <div className="cluster-classification">
              <h2 className="cluster-title text-blue">{user?.cluster}</h2>
              <p className="cluster-description text-secondary">
                {user?.clusterDescription}
              </p>
            </div>

            <div className="summary-insight bg-primary-light">
              <Lightbulb size={20} className="text-primary insight-icon" />
              <div className="insight-text">
                <p className="font-semibold text-primary">Key Insight</p>
                <p className="text-sm mt-1">
                  You spend 12% less on non-essentials compared to peers in this cluster, but your housing costs are slightly above average.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="chart-card">
          <CardHeader>
            <CardTitle>User Cluster Distribution</CardTitle>
          </CardHeader>
          <CardContent className="donut-chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={clusterData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {clusterData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="cluster-legend">
              {clusterData.map(cluster => (
                <div key={cluster.name} className="legend-item">
                  <div className="legend-color" style={{ backgroundColor: cluster.color }}></div>
                  <span className="legend-label">{cluster.name}</span>
                  <span className="legend-value font-semibold">{cluster.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
