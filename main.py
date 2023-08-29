from fastapi import FastAPI
from user import router as user_router
from post import router as post_router

app = FastAPI()

app.include_router(user_router.router)
app.include_router(post_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
