from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, status
from pymongo import ReturnDocument
from app.database import topic_collection, subscriber_collection
from app.models.topic import CreateTopicModel, ListTopic, SubscribeUpdateTopic, TopicModel

router = APIRouter(
    prefix="/topic",
    tags=["topic"],
    responses={404: {"description": "Not found"}},
)


@router.get("/",
            response_model=ListTopic,
            status_code=status.HTTP_200_OK,
            response_model_by_alias=False,
            )
async def list_topics():
    topics = await topic_collection.find().to_list(1000)
    return ListTopic(topics=topics)


@router.get("/{topic_id}", response_model=TopicModel)
async def get_topic(topic_id: str):
    return {"username": "fakecurrentuser"}


@router.post("/",
             response_model=TopicModel,
             status_code=status.HTTP_201_CREATED,
             response_model_by_alias=False,
             )
async def create_topic(data: TopicModel = Body(...)):
    now = datetime.now()
    data.created = now
    data.updated = now
    new_topic = await topic_collection.insert_one(
        data.model_dump(by_alias=True, exclude=["id", "subscribes"])
    )
    created_new_topic = await topic_collection.find_one(
        {"_id": new_topic.inserted_id}
    )
    return created_new_topic


@router.patch("/{topic_id}",
              response_model=TopicModel,
              status_code=status.HTTP_200_OK,
              response_model_by_alias=False,
              description="update topic name"
              )
async def update_topic(topic_id: str, data: CreateTopicModel = Body(...)):
    topic = {
        k: v for k, v in data.model_dump(by_alias=True).items() if v is not None
    }

    if len(topic) >= 1:
        topic["updated"] = datetime.now()

        update_result = await topic_collection.find_one_and_update(
            {"_id": ObjectId(topic_id)},
            {"$set": topic},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(
                status_code=404, detail=f"Student {topic_id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_topic := await topic_collection.find_one({"_id": topic_id})) is not None:
        return existing_topic

    raise HTTPException(
        status_code=404, detail=f"Topic {topic_id} not found")


@router.patch("/subscribe/{topic_id}",
              response_model=TopicModel,
              status_code=status.HTTP_200_OK,
              response_model_by_alias=False,
              description="Subscribe a topic"
              )
async def subscribe_topic(topic_id: str, data: SubscribeUpdateTopic = Body(...)):

    if len(data.subscribe_ids) >= 1:
        existing_topic = await topic_collection.find_one({"_id": ObjectId(topic_id)})
        if not existing_topic:
            raise HTTPException(
                status_code=404, detail=f"Topic {topic_id} not found")

        existing_sub_ids = set(e["_id"]
                               for e in existing_topic.get("subscribes", []))

        updatable_sub_ids = []
        for subscribe_id in data.subscribe_ids:
            if subscribe_id not in existing_sub_ids:
                updatable_sub_ids.append(ObjectId(subscribe_id))
        subscribers = await subscriber_collection.find({"_id": {"$in": updatable_sub_ids}}).to_list(1000)
        appendable_sub_obj = []
        for sub in subscribers:
            appendable_sub_obj.append(
                {
                    "_id": sub["_id"],
                    "name": sub["name"],
                    "routing_url": sub["routing_url"]
                }
            )
        if appendable_sub_obj:
            update_result = await topic_collection.find_one_and_update(
                {"_id": ObjectId(topic_id)},
                {
                    "$set": {"updated": datetime.now()},
                    "$push": {"subscribes": {"$each": appendable_sub_obj}}
                },
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                return update_result
            else:
                raise HTTPException(
                    status_code=404, detail=f"Topic {topic_id} not found")

    if (existing_topic := await topic_collection.find_one({"_id": topic_id})) is not None:
        return existing_topic

    raise HTTPException(status_code=404, detail=f"Topic {id} not found")


@router.patch("/unsubscribe/{topic_id}",
              response_model=TopicModel,
              status_code=status.HTTP_200_OK,
              response_model_by_alias=False,
              description="Unubscribe a topic"
              )
async def unsubscribe_topic(topic_id: str, data: SubscribeUpdateTopic = Body(...)):

    if len(data.subscribe_ids) >= 1:
        existing_topic = await topic_collection.find_one({"_id": ObjectId(topic_id)})
        if not existing_topic:
            raise HTTPException(
                status_code=404, detail=f"Topic {topic_id} not found")

        existing_sub_ids = set(e["_id"]
                               for e in existing_topic.get("subscribes", []))

        removable_sub_ids = []
        for subscribe_id in data.subscribe_ids:
            if ObjectId(subscribe_id) in existing_sub_ids:
                removable_sub_ids.append(ObjectId(subscribe_id))
        if removable_sub_ids:
            update_result = await topic_collection.find_one_and_update(
                {"_id": ObjectId(topic_id)},
                {
                    "$set": {"updated": datetime.now()},
                    "$pull": {
                        "subscribes": {
                            "_id": {"$in": removable_sub_ids}
                        }
                    }
                },
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                return update_result
            else:
                raise HTTPException(
                    status_code=404, detail=f"Topic {topic_id} not found")

    if (existing_topic := await topic_collection.find_one({"_id": topic_id})) is not None:
        return existing_topic

    raise HTTPException(status_code=404, detail=f"Topic {id} not found")
