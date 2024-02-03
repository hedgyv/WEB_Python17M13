#____5.12.A&A_____________________________repository/users____________________________
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.
    
    :param email: str: Get the email from the request body
    :param db: AsyncSession: Pass in the database session
    :return: A user object or none if the email does not exist
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user

#____6.12.A&A_____________________________create_user____________________________
async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
        It takes a UserSchema object as input and returns the newly created user.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object, which is the same as the body
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

#____7.12.A&A_____9.12.A&A________________________________________________________________
async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the user's refresh token in the database.
    
    :param user: User: Identify the user that is being updated
    :param token: str | None: Specify that the token parameter can be either a string or none
    :param db: AsyncSession: Allow the function to commit changes to the database
    :return: Nothing, so the return type is none
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()
    
#__________________1.13.Email_______________________________________________________________________________________    
async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a user as confirmed by setting their confirmation field to True.
    
    :param email: str: Pass in the email address of the user who is confirming their account
    :param db: AsyncSession: Pass in the database session
    :return: None, but the type hint says it returns none
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmation = True
    await db.commit()

#____________________________5.13____cloudinary______________________________________    
async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.
    
    :param email: str: Get the user from the database
    :param url: str | None: Determine whether the user has an avatar or not
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user