from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from app.database import PyObjectId


class Subscriber(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    routing_url : str
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "test topic",
                "routing_url": "http://example.com"
            }
        },
    )

class UpdateSubscriber(BaseModel):
    name: Optional[str] = None
    routing_url: Optional[str] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "test topic",
                "routing_url": "http://example.com"
            }
        },
    )

class MiniSubscribe(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    routing_url : str

class ListMiniSubscribe(BaseModel):
    subscribes : list[MiniSubscribe] = Field(default_factory=list)

class ListSubscriber(BaseModel):
    subscribers : list[Subscriber] = Field(default_factory=list)