from fastapi import Depends, FastAPI

from app.dependencies import get_query_token, get_token_header
from app.routers import topic, message, subscriber

app = FastAPI(
    # dependencies=[Depends(get_query_token)]
    )


app.include_router(topic.router)
app.include_router(message.router)
app.include_router(subscriber.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}