from fastapi import FastAPI
from user import router as user_router

app = FastAPI()

app.include_router(user_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
