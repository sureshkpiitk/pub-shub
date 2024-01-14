from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pymongo import ReturnDocument
from app.database import subscriber_collection
from app.dependencies import get_token_header
from app.models.subscriber import ListSubscriber, Subscriber, UpdateSubscriber

router = APIRouter(
    prefix="/subscriber",
    tags=["subscriber"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/",
            response_description="List of subscribers",
            response_model=ListSubscriber,
            status_code=status.HTTP_200_OK,
            response_model_by_alias=False,
            )
async def get_subscribers():
    subscribers = await subscriber_collection.find().to_list(1000)
    return ListSubscriber(subscribers=subscribers)


@router.get("/{subscriber_id}/",
            response_description="List of subscribers",
            response_model=Subscriber,
            status_code=status.HTTP_200_OK,
            response_model_by_alias=False,
            )
async def get_subscriber(subscriber_id):
    if (
        subscriber := await subscriber_collection.find_one({"_id": ObjectId(subscriber_id)})
    ) is not None:
        return subscriber
    raise HTTPException(status_code=404, detail=f"Subscriber {subscriber_id} not found")


@router.post("/",
             response_model=Subscriber,
             status_code=status.HTTP_201_CREATED,
             response_model_by_alias=False,
             )
async def create_subscriber(subscriber: Subscriber=Body(...)):
    now = datetime.now()
    subscriber.created = now
    subscriber.updated = now
    new_subscriber = await subscriber_collection.insert_one(
        subscriber.model_dump(by_alias=True, exclude=["id"])
    )
    created_subscriber = await subscriber_collection.find_one(
        {"_id": new_subscriber.inserted_id}
    )
    return created_subscriber


@router.patch("/{subscriber_id}",
              response_model=Subscriber,
              response_model_by_alias=False,
              )
async def update_subscriber(subscriber_id: str, subscribe: UpdateSubscriber=Body(...)):
    subscriber = {
        k: v for k, v in subscribe.model_dump(by_alias=True).items() if v is not None
    }
    subscriber["update"] = datetime.now()

    if len(subscriber) >= 1:
        update_result = await subscriber_collection.find_one_and_update(
            {"_id": ObjectId(subscriber_id)},
            {"$set": subscriber},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Student {id} not found")

    if (existing_subscriber := await subscriber_collection.find_one({"_id": subscriber_id})) is not None:
        return existing_subscriber

    raise HTTPException(status_code=404, detail=f"Subscribe {subscriber_id} not found")
