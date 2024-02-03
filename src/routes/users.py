#____________________________3.13____limiter___________________________________________________________________________________
import pickle

import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, File, HTTPException, Request, Depends, UploadFile, status, Path, Query, Security, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.repository import users as reps_users
from fastapi_limiter.depends import RateLimiter 
from src.conf.config import config
from src.database.db import get_db

router = APIRouter(prefix="/users", tags=["users"])

#____5.13___ініціалізація cloudinary__________________________
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.
    
    :param user: User: Get the user object from the database
    
    :return: The user object that is stored in the token
    :doc-author: Trelent
    """
    
    return user


#____________________________5.13____cloudinary___________________________________________________________________________________
@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    
    """
    The get_current_user function is used to get the current user from the database.
    
    :param file: UploadFile: Get the file from the request
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :param : Get the current user from the cache
    
    :return: The user object, but the avatar_url is not updated
    :doc-author: Trelent
    """
    
    public_id = f"Web17/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await reps_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    
    return user