export const CITIES = {
  amsterdam: {
    name: 'Amsterdam',
    slug: 'amsterdam',
    center: [52.3676, 4.9041],
    zoom: 12,
  },
  rome: {
    name: 'Rome',
    slug: 'rome',
    center: [41.9028, 12.4964],
    zoom: 12,
  },
  prague: {
    name: 'Prague',
    slug: 'prague',
    center: [50.0755, 14.4378],
    zoom: 12,
  },
};

export const getSentimentColor = (sentiment) => {
  if (sentiment == null) return '#9ca3af'; 
  
  if (sentiment >= 0.05) return '#10b981';
  
  if (sentiment >= -0.05) return '#f59e0b'; 
  
  return '#ef4444'; 
};
