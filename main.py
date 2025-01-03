import hashlib
from datetime import datetime, timedelta

import uvicorn
import validators
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import URL, SessionLocal, init_db
from rate_limit_helper import RedisRateLimiterMiddleware
from redis_helper import RedisClient
from schemas import URLBase, URLInfo

redis_helper = RedisClient()

app = FastAPI()
app.add_middleware(
    RedisRateLimiterMiddleware, redis_client=redis_helper, limit=3, window=5
)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def raise_bad_request(*args, **kwargs):
    raise HTTPException(status_code=400, detail=kwargs)


async def raise_not_found(*args, **kwargs):
    raise HTTPException(status_code=404, detail=kwargs)


@app.post("/create-url", response_model=URLInfo)
async def create_url(url: URLBase, db: AsyncSession = Depends(get_db)):
    if not validators.url(url.original_url) or len(url.original_url) > 2048:
        data = {
            "short_url": "",
            "expiration_date": None,
            "success": False,
            "reason": "Your provided URL is not valid",
        }
        await raise_bad_request(**data)

    m = hashlib.md5()
    m.update(url.original_url.encode("utf-8"))

    data = {
        "short_url": m.hexdigest(),
        "expiration_date": datetime.now() + timedelta(days=30),
        "success": True,
        "reason": "",
    }

    result = await db.execute(
        select(URL).where(URL.original_url == url.original_url),
    )
    existing_url = result.scalar_one_or_none()

    if existing_url:
        existing_url.expiration_date = data["expiration_date"]
        await db.commit()
        return data

    new_url = URL(
        original_url=url.original_url,
        short_url=data["short_url"],
        expiration_date=data["expiration_date"],
    )
    db.add(new_url)
    await db.commit()

    return data


@app.get("/{short_key}")
async def redirect_url(short_key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(URL).where(URL.short_url == short_key))
    existing_url = result.scalar_one_or_none()
    if existing_url:
        # Redirect the user to the original URL
        return RedirectResponse(existing_url.original_url)
    await raise_not_found(message="Your provided shorten URL does not exist")


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
