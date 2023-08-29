from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from post import models
from post import schemas
from user.schemas import User, UserSingle


async def get_all_posts(db: AsyncSession):
    query = select(models.Post).options(selectinload(models.Post.author))

    post_list = await db.execute(query)

    formatted_posts = []
    for post in post_list.scalars():
        formatted_post = {
            "id": post.id,
            "author_id": post.author_id,
            "author": post.author,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": post.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        formatted_posts.append(formatted_post)

    return formatted_posts


async def post_selector_for_update_or_delete(
    post_id: int, user: User, db: AsyncSession
):
    query = (
        select(models.Post)
        .where(models.Post.author_id == user.id)
        .where(models.Post.id == post_id)
    )

    post = await db.execute(query)

    return post.scalar_one_or_none()


async def post_selector(post_id: int, db: AsyncSession):
    query = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = await db.execute(query)
    return post.scalar_one_or_none()


async def get_single_post(post_id: int, db: AsyncSession):
    post = await post_selector(post_id=post_id, db=db)

    if post is None:
        raise HTTPException(status_code=404, detail="Post does not exist")

    formatted_post = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": post.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "author_id": post.author_id,
        "author": post.author,
    }

    return formatted_post


async def create_post(user: UserSingle, post: schemas.PostCreate, db: AsyncSession):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        author_id=user.id,
        author=user,
    )

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    return db_post


async def delete_post(post_id: int, user: User, db: AsyncSession):
    post = await post_selector_for_update_or_delete(post_id, user, db)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()


async def update_post(
    post_id: int, post: schemas.PostCreate, user: User, db: AsyncSession
):
    db_post = await post_selector_for_update_or_delete(post_id, user, db)

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db_post.title = post.title
    db_post.content = post.content
    db_post.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_post)

    return db_post
