from datetime import datetime
import asyncio
import aiohttp
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status, BackgroundTasks
from app.database import message_collection, topic_collection
from app.dependencies import get_token_header
from app.models.message import Message

router = APIRouter(
    prefix="/message",
    tags=["message"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)



@router.get("/",
            response_description="List of subscribers",
            response_model=list[Message],
            status_code=status.HTTP_200_OK,
            response_model_by_alias=False,
            )
async def get_messages():
    messages = await message_collection.find().to_list(1000)
    return messages

async def _send_message(session: aiohttp.ClientSession, url:str,  message: dict):
    result = await session.post(url, data=message)
    print(result)
    return result

async def send_message_to_subscribers(message: dict):
    print("async task started")
    await asyncio.sleep(10)
    
    existing_topic = await topic_collection.find_one({"_id": ObjectId(message["topic_id"])})
    
    if not existing_topic: 
        raise Exception("Not found task id")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for subscriber in existing_topic.get("subscribes"):
            tasks.append(_send_message(session, subscriber["routing_url"], message["message"]))
        
        result = await asyncio.gather(*tasks)
        print("task finished")
        return result


@router.post(
    "/",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def send_message(background_task: BackgroundTasks, data: Message = Body(...)):
    
    now = datetime.now()
    data.created = now
    data.updated = now
    new_subscriber = await message_collection.insert_one(
        data.model_dump(by_alias=True, exclude=["id"])
    )
    created_message = await message_collection.find_one(
        {"_id": new_subscriber.inserted_id}
    )
    background_task.add_task(send_message_to_subscribers, created_message)
    print("response sent")

    return created_message
