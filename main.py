import hashlib
from datetime import datetime, timedelta

import uvicorn
import validators
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from rate_limit_helper import RedisRateLimiterMiddleware
from redis_helper import RedisClient
from schemas import URLBase, URLInfo

redis_helper = RedisClient()

app = FastAPI()
app.add_middleware(
    RedisRateLimiterMiddleware, redis_client=redis_helper, limit=3, window=5
)

# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


@app.post("/create-url", response_model=URLInfo)
# def create_url(url: URLBase, db: Session = Depends(get_db)):
async def create_url(url: URLBase):
    if not validators.url(url.original_url) or len(url.original_url) > 2048:
        raise_bad_request(message="Your provided URL is not valid")

    data = {}
    m = hashlib.md5()
    m.update(url.original_url.encode("utf-8"))
    data["short_url"] = m.hexdigest()
    data["expiration_date"] = datetime.now() + timedelta(days=30)
    data["success"] = True
    data["reason"] = ""
    redis_helper.set(data["short_url"], url.original_url, ex=30)
    return data


@app.get("/{short_key}")
async def redirect_url(short_key: str):
    original_url = redis_helper.get(short_key)
    print(original_url)
    if original_url:
        # Redirect the user to the original URL
        return RedirectResponse(original_url)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
