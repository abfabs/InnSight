# backend/data/geojson_processor.py

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeoJSONProcessor:
    """Processes GeoJSON files for neighborhood boundaries."""
    
    def __init__(self):
        self.geojson_data = None
    
    def load_geojson(self, filepath: Path) -> Dict:
        """
        Load GeoJSON file.
        
        Args:
            filepath: Path to GeoJSON file
            
        Returns:
            GeoJSON data as dictionary
        """
        logger.info(f"Loading GeoJSON from {filepath}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.geojson_data = json.load(f)
            
            logger.info(f"GeoJSON loaded successfully")
            logger.info(f"  Type: {self.geojson_data.get('type')}")
            
            if 'features' in self.geojson_data:
                logger.info(f"  Features: {len(self.geojson_data['features'])}")
            
            return self.geojson_data
        
        except FileNotFoundError:
            logger.error(f"GeoJSON file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid GeoJSON format: {e}")
            raise
    
    def validate_geojson(self) -> bool:
        """
        Validate GeoJSON structure.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.geojson_data:
            logger.error("No GeoJSON data loaded")
            return False
        
        # Check for required fields
        if self.geojson_data.get('type') != 'FeatureCollection':
            logger.error("GeoJSON must be a FeatureCollection")
            return False
        
        if 'features' not in self.geojson_data:
            logger.error("GeoJSON missing 'features' field")
            return False
        
        # Validate each feature
        for i, feature in enumerate(self.geojson_data['features']):
            if feature.get('type') != 'Feature':
                logger.warning(f"Feature {i} is not of type 'Feature'")
            
            if 'geometry' not in feature:
                logger.warning(f"Feature {i} missing 'geometry'")
            
            if 'properties' not in feature:
                logger.warning(f"Feature {i} missing 'properties'")
        
        logger.info("GeoJSON validation complete")
        return True
    
    def extract_neighbourhoods(self) -> List[str]:
        """
        Extract list of neighbourhood names from GeoJSON.
        
        Returns:
            List of neighbourhood names
        """
        if not self.geojson_data:
            logger.error("No GeoJSON data loaded")
            return []
        
        neighbourhoods = []
        
        for feature in self.geojson_data.get('features', []):
            properties = feature.get('properties', {})
            neighbourhood = properties.get('neighbourhood')
            
            if neighbourhood:
                neighbourhoods.append(neighbourhood)
        
        logger.info(f"Extracted {len(neighbourhoods)} neighbourhoods from GeoJSON")
        
        return neighbourhoods
    
    def get_neighbourhood_bounds(self, neighbourhood_name: str) -> Dict[str, float]:
        """
        Get bounding box for a specific neighbourhood.
        
        Args:
            neighbourhood_name: Name of the neighbourhood
            
        Returns:
            Dictionary with min/max lat/lon
        """
        if not self.geojson_data:
            logger.error("No GeoJSON data loaded")
            return {}
        
        for feature in self.geojson_data.get('features', []):
            properties = feature.get('properties', {})
            
            if properties.get('neighbourhood') == neighbourhood_name:
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                if not coordinates:
                    continue
                
                # Flatten coordinates (handle MultiPolygon)
                all_coords = []
                
                if geometry.get('type') == 'Polygon':
                    for ring in coordinates:
                        all_coords.extend(ring)
                elif geometry.get('type') == 'MultiPolygon':
                    for polygon in coordinates:
                        for ring in polygon:
                            all_coords.extend(ring)
                
                if not all_coords:
                    continue
                
                # Calculate bounds
                lons = [coord[0] for coord in all_coords]
                lats = [coord[1] for coord in all_coords]
                
                return {
                    'min_lon': min(lons),
                    'max_lon': max(lons),
                    'min_lat': min(lats),
                    'max_lat': max(lats),
                    'center_lon': sum(lons) / len(lons),
                    'center_lat': sum(lats) / len(lats)
                }
        
        logger.warning(f"Neighbourhood '{neighbourhood_name}' not found in GeoJSON")
        return {}
    
    def simplify_geojson(self, precision: int = 5) -> Dict:
        """
        Simplify GeoJSON by reducing coordinate precision.
        
        Args:
            precision: Number of decimal places for coordinates
            
        Returns:
            Simplified GeoJSON
        """
        if not self.geojson_data:
            logger.error("No GeoJSON data loaded")
            return {}
        
        def round_coords(coords, depth=0):
            """Recursively round coordinates."""
            if isinstance(coords[0], (int, float)):
                # Base case: this is a coordinate pair [lon, lat]
                return [round(coords[0], precision), round(coords[1], precision)]
            else:
                # Recursive case: list of coordinates
                return [round_coords(c, depth+1) for c in coords]
        
        simplified = self.geojson_data.copy()
        
        for feature in simplified.get('features', []):
            geometry = feature.get('geometry', {})
            if 'coordinates' in geometry:
                geometry['coordinates'] = round_coords(geometry['coordinates'])
        
        logger.info(f"GeoJSON simplified to {precision} decimal places")
        
        return simplified
    
    def save_geojson(self, filepath: Path, data: Dict = None):
        """
        Save GeoJSON to file.
        
        Args:
            filepath: Path to save GeoJSON
            data: GeoJSON data (uses loaded data if None)
        """
        data = data or self.geojson_data
        
        if not data:
            logger.error("No GeoJSON data to save")
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"GeoJSON saved to {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to save GeoJSON: {e}")
            raise
    
    def prepare_for_mongodb(self) -> List[Dict]:
        """
        Prepare GeoJSON features for MongoDB storage.
        
        Returns:
            List of documents ready for MongoDB insertion
        """
        if not self.geojson_data:
            logger.error("No GeoJSON data loaded")
            return []
        
        documents = []
        
        for feature in self.geojson_data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            doc = {
                'neighbourhood': properties.get('neighbourhood'),
                'neighbourhood_group': properties.get('neighbourhood_group'),
                'geometry': geometry,
                'type': 'neighbourhood'
            }
            
            # Add bounds for quick lookup
            neighbourhood_name = properties.get('neighbourhood')
            if neighbourhood_name:
                bounds = self.get_neighbourhood_bounds(neighbourhood_name)
                if bounds:
                    doc['bounds'] = bounds
            
            documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} neighbourhood documents for MongoDB")
        
        return documents
