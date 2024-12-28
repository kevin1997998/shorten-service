import validators
from math import ceil
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi import status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from schemas import URLBase, URLInfo
import uvicorn
#from database import SessionLocal, engine, Base
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

async def custom_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )

async def service_name_identifier(request: Request):
    service = request.headers.get("Service-Name")
    return service

@asynccontextmanager
async def lifespan(_: FastAPI):
    r = redis.from_url("redis://127.0.0.1:6379", encoding="utf8")
    #r = redis.Redis(host='localhost', port=6379, decode_responses=True) 
    await FastAPILimiter.init(
        redis=r,
        identifier=service_name_identifier,
        http_callback=custom_callback,
    )
    yield
    await FastAPILimiter.close()

app = FastAPI(lifespan=lifespan)
#Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import string
import redis
import hashlib

BASE62 = string.digits + string.ascii_letters
r = redis.Redis(host='localhost', port=6379, decode_responses=True) 

async def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

@app.post("/create-url", response_model=URLInfo, dependencies=[Depends(RateLimiter(times=1, seconds=5))])
#def create_url(url: URLBase, db: Session = Depends(get_db)):
async def create_url(url: URLBase):
    if not validators.url(url.original_url) or len(url.original_url) > 2048:
        raise_bad_request(message="Your provided URL is not valid")
    
    data = {}
    #data["short_url"] = encode_base62(url.original_url)
    m = hashlib.md5()
    m.update(url.original_url.encode("utf-8"))
    data["short_url"] = m.hexdigest()
    data["expiration_date"] = datetime.now() + timedelta(days = 30)
    data["success"] = True
    data["reason"] = ""
    r.set(data["short_url"], url.original_url)

    return data

@app.get("/{short_key}", dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def redirect_url(short_key: str):
    original_url = r.get(short_key)
    print(original_url)
    if original_url:
        # Redirect the user to the original URL
        return RedirectResponse(original_url)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)