import React, { useState, useEffect } from 'react';
import { Download, Image as ImageIcon } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { ApiService } from '../../services/api';

export const VisualizationsGallery: React.FC = () => {
  const [images, setImages] = useState<{ filename: string; title: string; }[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchImages = async () => {
      setIsLoading(true);
      try {
        const data = await ApiService.getVisualizationsList();
        // Assuming API returns array like [{ filename: 'heatmap.png', title: 'Feature Heatmap' }]
        setImages(data);
      } catch (err) {
        // Fallback for demonstration if endpoint is not built yet
        setImages([
          { filename: 'mock_scatter.png', title: 'Anomaly Scatter Distribution' },
          { filename: 'mock_heatmap.png', title: 'Correlation Heatmap' },
          { filename: 'mock_cluster.png', title: 'K-Means Cluster Boundaries' }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchImages();
  }, []);

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="section-header">
        <h2 className="section-title">Static Visualizations</h2>
        <p className="section-subtitle text-secondary">Pre-rendered Matplotlib and Seaborn charts from the ML Backend.</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20 text-muted animate-pulse">Loading gallery...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((img, i) => (
            <Card key={i} className="overflow-hidden group flex flex-col relative h-[300px]">
              <CardContent className="p-0 flex-1 relative bg-bg flex items-center justify-center">
                {/* Fallback styling explicitly to handle missing images elegantly */}
                <div className="w-full h-full flex items-center justify-center relative overflow-hidden">
                  <span className="text-muted flex flex-col items-center gap-2 z-0">
                    <ImageIcon size={32} opacity={0.5} />
                    <span className="text-xs uppercase">{img.filename}</span>
                  </span>
                  <img 
                    src={ApiService.getVisualizationImageUrl(img.filename)}
                    alt={img.title}
                    className="absolute inset-0 w-full h-full object-contain z-10 transition-opacity"
                    onError={(e) => { e.currentTarget.style.opacity = '0'; }}
                  />
                </div>
                
                {/* Hover Overlay */}
                <div className="absolute inset-0 bg-sidebar/80 opacity-0 group-hover:opacity-100 transition-opacity z-20 flex flex-col justify-end p-4">
                   <h4 className="text-card font-semibold text-lg mb-2">{img.title}</h4>
                   <Button variant="primary" size="sm" icon={<Download size={14} />} className="w-full justify-center text-sm">Download</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
