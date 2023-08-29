from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_async_session
from post import crud
from post import schemas
from user.crud import get_current_user
from user.schemas import User, UserSingle

router = APIRouter(prefix="/api", tags=["post"])


@router.get("/posts/", response_model=list[schemas.Post])
async def read_posts(db: AsyncSession = Depends(get_async_session)):
    return await crud.get_all_posts(db=db)


@router.get("/posts/{post_id}", status_code=200, response_model=schemas.PostSingle)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    db_post = await crud.get_single_post(post_id=post_id, db=db)

    return db_post


@router.post("/posts/", response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    user: UserSingle = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await crud.create_post(user=user, db=db, post=post)


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await crud.delete_post(post_id, user, db)
    return {"message": "Post Successfully Deleted"}


@router.put("/posts/{post_id}", status_code=200)
async def update_post(
    post_id: int,
    post: schemas.PostCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await crud.update_post(post_id, post, user, db)
    return {"message": "Post Successfully Updated"}
