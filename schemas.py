"""
Database Schemas for Travel App

Each Pydantic model represents a collection in MongoDB. The collection name
is the lowercase of the class name (e.g., Itinerary -> "itinerary").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import date


class Destination(BaseModel):
    """
    Curated destinations
    Collection: "destination"
    """
    name: str = Field(..., description="City or place name")
    country: str = Field(..., description="Country name")
    image: Optional[str] = Field(None, description="Hero image URL")
    tagline: Optional[str] = Field(None, description="Short marketing tagline")


class ItineraryItem(BaseModel):
    """Single item in an itinerary, e.g., flight, hotel, or activity"""
    type: Literal["flight", "hotel", "activity"]
    title: str
    date: Optional[date] = None
    time: Optional[str] = Field(None, description="Time like 08:30")
    notes: Optional[str] = None


class Itinerary(BaseModel):
    """
    Saved itineraries
    Collection: "itinerary"
    """
    name: str = Field(..., description="Trip name")
    owner_email: EmailStr = Field(..., description="Owner email")
    items: List[ItineraryItem] = Field(default_factory=list)


class Subscriber(BaseModel):
    """
    Newsletter subscribers
    Collection: "subscriber"
    """
    email: EmailStr


class Message(BaseModel):
    """
    Contact messages
    Collection: "message"
    """
    name: str
    email: EmailStr
    message: str
