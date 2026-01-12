"""
InnSight Listing Schema
Pydantic models for API validation and documentation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Listing(BaseModel):
    """
    Core Airbnb listing model
    Matches your listings_clean.csv + sentiment data
    """
    listing_id: str = Field(..., description="Unique Airbnb listing ID")
    listing_name: str = Field(..., description="Listing title")
    host_id: str = Field(..., description="Host ID")
    host_name: str = Field(..., description="Host display name")
    neighbourhood: str = Field(..., description="Neighborhood name")
    city: str = Field(..., description="City (lowercase)")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    property_type: str = Field(..., description="Property type")
    room_type: str = Field(..., description="Room type")
    price: float = Field(..., gt=0, description="Price per night")
    minimum_nights: int = Field(..., ge=1, description="Min nights")
    maximum_nights: int = Field(..., ge=1, description="Max nights")
    accommodates: int = Field(..., ge=1, description="Guests accommodated")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    beds: Optional[int] = Field(None, description="Number of beds")
    number_of_reviews: int = Field(default=0, description="Total reviews")
    review_scores_rating: Optional[float] = Field(None, description="Review score 0-5")
    sentiment_mean: float = Field(default=0.0, description="Sentiment score -1 to 1")
    
    class Config:
        # MongoDB compatibility
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ListingResponse(BaseModel):
    """API response model (subset for listings endpoint)"""
    listing_id: str
    listing_name: str
    host_name: str
    neighbourhood: str
    latitude: float
    longitude: float
    room_type: str
    price: float
    number_of_reviews: int
    review_scores_rating: Optional[float] = None
    sentiment_mean: float


# Example data (for testing/docs)
EXAMPLE_LISTING = {
    "listing_id": "26755",
    "listing_name": "Central Prague Old Town Top Floor",
    "host_id": "113902",
    "host_name": "Daniel+Bea",
    "neighbourhood": "Praha 1",
    "city": "prague",
    "latitude": 50.08729,
    "longitude": 14.43179,
    "property_type": "Entire rental unit",
    "room_type": "Entire home/apt",
    "price": 2272.0,
    "minimum_nights": 3,
    "maximum_nights": 700,
    "accommodates": 4,
    "bedrooms": 1,
    "beds": 2,
    "number_of_reviews": 440,
    "review_scores_rating": 4.95,
    "sentiment_mean": 0.6214
}
