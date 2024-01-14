import os
from typing import Annotated
import motor.motor_asyncio
from pydantic import BeforeValidator


client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGODB_URL", "localhost"))

db = client.get_database("pub-sub")
topic_collection = db.get_collection("topic")
message_collection = db.get_collection("message")
subscriber_collection = db.get_collection("subscriber")

PyObjectId = Annotated[str, BeforeValidator(str)]

