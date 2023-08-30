from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from dependencies import get_async_session
from post import crud
from post import schemas
from user.crud import get_current_user
from user.schemas import User, UserSingle

router = APIRouter(prefix="/api", tags=["post"])


@router.get("/posts/", response_model=list[schemas.Post])
async def read_posts(db: AsyncSession = Depends(get_async_session)):
    return await crud.get_all_posts(db=db)


@router.get(
    "/posts/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.PostSingle,
)
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


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await crud.delete_post(post_id, user, db)
    return {"message": "Post Successfully Deleted"}


@router.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    post: schemas.PostCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await crud.update_post(post_id, post, user, db)
    return {"message": "Post Successfully Updated"}


@router.get("/comments/", response_model=list[schemas.Comment])
async def read_comments(db: AsyncSession = Depends(get_async_session)):
    return await crud.get_all_comments(db=db)


@router.get("/posts/{post_id}/comments/", response_model=list[schemas.Comment])
async def read_posts_with_comments(
    post_id: int, db: AsyncSession = Depends(get_async_session)
) -> list[schemas.Comment]:
    db_post = await crud.get_single_post(db=db, post_id=post_id)

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return await crud.get_comments_by_post(db=db, post_id=post_id)


@router.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    user: UserSingle = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    db_post = await crud.is_post_owner(post_id, user.id, db)

    if db_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot comment on your own post.",
        )

    return await crud.create_comment(user=user, db=db, comment=comment)
