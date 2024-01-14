from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from app.database import PyObjectId

class Message(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    topic_id: str
    message: dict
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "Object id",
                "topic_id": "Object id",
                "message": {"key": "value"}
            }
        },
    )