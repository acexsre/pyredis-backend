from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aioredis, uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global redis
    redis = await aioredis.from_url("redis://localhost")

@app.on_event("shutdown")
async def shutdown_event():
    redis.close()
    await redis.wait_closed()

@app.get("/post/{postid}")
async def get_post(postid: int):
    post = await redis.get(f"post{postid}")
    return {"post": post.decode("utf-8")}

@app.post("/seed")
async def multi_set():
    data={"post1": "this is my first post with redis","post2": "this is my second post with redis","post3": "this is my third post with redis"}
    try:
        async with redis.pipeline(transaction=True) as pipe:
            for key,value in data.items():
                await pipe.set(key, value).execute()
        return {"message": "DB seeding completed successfully"}
    except:
        return {"message": "DB seeding unsuccessful"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
