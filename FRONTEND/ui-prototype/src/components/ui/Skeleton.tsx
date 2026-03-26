import React from 'react';
import './Skeleton.css';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'rectangular' | 'circular' | 'text';
  width?: string | number;
  height?: string | number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'rectangular',
  width,
  height,
  className = '',
  ...props
}) => {
  const style = {
    width: width,
    height: height,
  };

  return (
    <div
      className={`skeleton skeleton-${variant} ${className}`}
      style={style}
      {...props}
    />
  );
};
