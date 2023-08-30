from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from config import SECRET_KEY, ALGORITHM
from dependencies import db_dependency, get_async_session
from user import schemas, crud, models
from user.security import verify_password


router = APIRouter(prefix="/api", tags=["user"])


@router.post("/user/register/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: db_dependency) -> schemas.User:
    return await crud.create_user(db=db, user=user)


@router.post("/user/token/", response_model=schemas.Token)
async def login_for_tokens(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Token:
    user = await crud.get_user_by_email(db, form_data.username)

    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token, refresh_token = crud.create_tokens(
        {"user_id": user.id, "sub": user.email}
    )

    return schemas.Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/user/refresh-token/", response_model=schemas.TokenRefresh)
async def refresh_token(refresh_token: str = Form(...)) -> schemas.TokenRefresh:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate refresh token")

    user = models.User(id=user_id, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    access_token, _ = crud.create_tokens({"user_id": user.id, "sub": user.email})

    return schemas.TokenRefresh(access_token=access_token, token_type="bearer")


@router.get("/user/me/", response_model=schemas.UserResponse)
async def get_user_profile(
    current_user: models.User = Depends(crud.get_current_user),
) -> schemas.UserResponse:
    formatted_registered_at = current_user.registered_at.strftime("%Y-%m-%d %H:%M:%S")

    user_response = schemas.UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        registered_at=formatted_registered_at,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )

    return user_response
