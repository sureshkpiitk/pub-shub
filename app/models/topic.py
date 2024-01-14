from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.database import PyObjectId
from app.models.subscriber import ListMiniSubscribe, MiniSubscribe


class TopicModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    subscribes: list[MiniSubscribe] = Field(default_factory=list)
    created : datetime = Field(default_factory=datetime.now)
    updated : datetime = Field(default_factory=datetime.now)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Topic",
                "created": datetime.now(),
                "updated": datetime.now(),
                "subscribes": []
            }
        },
    )
    
class SubscribeUpdateTopic(BaseModel):
    subscribe_ids: list[str] = Field(default_factory=list)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Topic",
                "subscribe_ids": []
            }
        },
    )

class CreateTopicModel(BaseModel):
    name: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Topic",
            }
        },
    )

class ListTopic(BaseModel):
    topics :list[TopicModel]
