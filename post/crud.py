from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from post import models
from post import schemas

from user.schemas import User, UserSingle


async def get_all_posts(db: AsyncSession) -> list[dict[str, Any]]:

    query = select(models.Post).options(selectinload(models.Post.owner))

    post_list = await db.execute(query)

    formatted_posts = []
    for post in post_list.scalars():
        formatted_post = {
            "id": post.id,
            "owner_id": post.owner_id,
            "owner": post.owner,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": post.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        formatted_posts.append(formatted_post)

    return formatted_posts


async def post_selector_for_update_or_delete(
    post_id: int, user: User, db: AsyncSession
) -> models.Post:

    query = (
        select(models.Post)
        .where(models.Post.owner_id == user.id)
        .where(models.Post.id == post_id)
    )

    post = await db.execute(query)

    return post.scalar_one_or_none()


async def post_selector(post_id: int, db: AsyncSession) -> models.Post:

    query = (
        select(models.Post)
        .options(selectinload(models.Post.owner))
        .where(models.Post.id == post_id)
    )
    post = await db.execute(query)
    return post.scalar_one_or_none()


async def get_single_post(post_id: int, db: AsyncSession) -> dict[str, str | int | Any]:

    post = await post_selector(post_id=post_id, db=db)

    if post is None:
        raise HTTPException(status_code=404, detail="Post does not exist")

    formatted_post = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": post.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "owner_id": post.owner_id,
        "owner": post.owner,
    }

    return formatted_post


async def create_post(
    user: UserSingle, post: schemas.PostCreate, db: AsyncSession
) -> models.Post:

    db_post = models.Post(
        title=post.title,
        content=post.content,
        owner_id=user.id,
        owner=user,
    )

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    return db_post


async def delete_post(post_id: int, user: User, db: AsyncSession) -> None:

    post = await post_selector_for_update_or_delete(post_id, user, db)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    await db.delete(post)
    await db.commit()


async def update_post(
    post_id: int, post: schemas.PostCreate, user: User, db: AsyncSession
) -> models.Post:

    db_post = await post_selector_for_update_or_delete(post_id, user, db)

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    db_post.title = post.title
    db_post.content = post.content
    db_post.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_post)

    return db_post


async def get_all_comments(db: AsyncSession) -> list[dict[str, Any]]:

    query = (
        select(models.Comment)
        .options(selectinload(models.Comment.post))
        .options(selectinload(models.Comment.author))
    )

    comment_list = await db.execute(query)

    formatted_comments = []
    for comment in comment_list.scalars():
        formatted_comment = {
            "id": comment.id,
            "author_id": comment.author_id,
            "author": comment.author,
            "post_id": comment.post_id,
            "post": comment.post,
            "commentary": comment.commentary,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": comment.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        formatted_comments.append(formatted_comment)

    return formatted_comments


async def get_comments_by_post(db: AsyncSession, post_id: int) -> list[models.Comment]:

    query = (
        select(models.Comment)
        .options(selectinload(models.Comment.post))
        .options(selectinload(models.Comment.author))
        .where(models.Comment.post_id == post_id)
    )
    comments = await db.execute(query)

    return [comment[0] for comment in comments.fetchall()]


async def get_post_by_id(db: AsyncSession, post_id: int) -> models.Post:

    query = select(models.Post).where(models.Post.id == post_id)
    post = await db.execute(query)

    return post.scalar_one_or_none()


async def is_post_owner(post_id: int, user_id: int, db: AsyncSession) -> bool:

    post = await get_post_by_id(db, post_id)
    if post:
        return post.owner_id == user_id

    return False


async def create_comment(
    user: UserSingle, comment: schemas.CommentCreate, db: AsyncSession,
) -> models.Comment:

    post = await db.execute(
        models.Post.__table__.select().where(models.Post.id == comment.post_id)
    )

    if post.fetchone() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    db_comment = models.Comment(**comment.model_dump(), author_id=user.id)

    try:
        db_comment.post_id = comment.post_id
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment",
        )

    return db_comment


async def comment_selector_for_update_or_delete(
    post_id: int, comment_id: int, user: User, db: AsyncSession
) -> models.Comment:

    query = (
        select(models.Comment)
        .where(models.Comment.author_id == user.id)
        .where(models.Comment.post_id == post_id)
        .where(models.Comment.id == comment_id)
    )

    comment = await db.execute(query)

    return comment.scalar_one_or_none()


async def update_comment_for_post(
    post_id: int,
    comment_id: int,
    updated_comment: schemas.CommentUpdate,
    db: AsyncSession,
    user: User,
) -> models.Comment:

    db_post = await get_post_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    db_comment = await comment_selector_for_update_or_delete(
        post_id, comment_id, user, db
    )

    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    db_comment.commentary = updated_comment.commentary
    db_comment.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_comment)

    return db_comment


async def delete_comment_for_post(
    post_id: int, comment_id: int, user: User, db: AsyncSession
) -> None:

    db_post = await get_post_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    db_comment = await comment_selector_for_update_or_delete(
        post_id, comment_id, user, db
    )

    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    await db.delete(db_comment)
    await db.commit()
