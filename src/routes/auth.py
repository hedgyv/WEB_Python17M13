from fastapi import APIRouter, HTTPException, Request, Depends, status, Path, Query, Security, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as reps_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email, send_email_reset_password

import re
from datetime import date, timedelta

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer() #____9.12.A&A____

#__________________2.12.A&A_______________________________________________________________________________________
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
#____6.12.A&A_____________________________реалізація____________________________
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a UserSchema object as input, and returns the newly created user.
        If an account with that email already exists, it raises an HTTP 409 Conflict error.
    
    :param body: UserSchema: Validate the request body
    :param bt: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get a database connection from the pool
    :return: A new user object
    :doc-author: Trelent
    """
    exist_user = await reps_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await reps_users.create_user(body, db)
    #__________________1.13.Email_______________________________________________________________________________________
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    #__________________1.13.Email_______________________________________________________________________________________|
    return new_user

#__________________2.12.A&A_______________________________________________________________________________________
@router.post("/login", response_model=TokenSchema)
#____7.12.A&A_____________________________реалізація____________________________
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes the email and password of the user as input, and returns an access token if authentication was successful.
    The access token can be used in subsequent requests to gain access to protected resources.
    
    :param body: OAuth2PasswordRequestForm: Receive the login information from the user
    :param db: AsyncSession: Get a database session
    :return: A dictionary with the access_token and refresh_token keys
    :doc-author: Trelent
    """
    user = await reps_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    #__________________1.13.Email_______________________________________________________________________________________
    if not user.confirmation:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    #__________________1.13.Email_______________________________________________________________________________________|
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "Ярослав Вдовенко"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await reps_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

#__________________2.12.A&A_______________________________________________________________________________________
@router.get('/refresh_token', response_model=TokenSchema)
#____9.12.A&A_____________________________реалізація____________________________
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, 
        a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request header
    :param db: AsyncSession: Connect to the database
    :return: A dictionary with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await reps_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await reps_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await reps_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

#__________________1.13.Email_______________________________________________________________________________________
@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the confirmation email and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist, returns an error message.
        If they do exist but their account has already been confirmed, we return a message saying so.
        Otherwise (if they exist and their account has not yet been confirmed), we update their record in our database 
        with confirmation=True.
    
    :param token: str: Get the token from the url
    :param db: AsyncSession: Connect to the database
    
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await reps_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmation:
        return {"message": "Your email is already confirmed"}
    await reps_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will confirm their email.
        The function takes in a RequestEmail object, which contains the user's email address. It then checks if the 
        user has already confirmed their account and returns an error message if they have. If not, it sends them an 
        email with a confirmation link.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get a database connection from the pool
    
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    user = await reps_users.get_user_by_email(body.email, db)

    if user.confirmation:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
#__________________1.13.Email_______________________________________________________________________________________|

@router.post("/forget-password")
async def forget_password(
    background_tasks: BackgroundTasks,
    fpr: RequestEmail,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    The forget_password function is used to send an email to the user with a link
    to reset their password. The function takes in the user's email address and sends
    an email containing a link that will expire after 15 minutes. The link contains
    a secret token which is used by the reset_password function to verify that it was 
    the same person who requested for their password to be changed.
    
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param fpr: RequestEmail: Get the email address from the request body
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Get the database connection from the pool
    
    :return: A jsonresponse object, which is a subclass of response
    :doc-author: Trelent
    """
    try:
        user = await reps_users.get_user_by_email(fpr.email, db)
        print('-----------------------')
        print(user.email,user.username)
        if user is None:
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="Invalid Email address")
            
        '''forget_url_link =  f"{config.APP_HOST}{settings.FORGET_PASSWORD_URL}/{secret_token}"
        
        email_body = { "company_name": settings.MAIL_FROM_NAME,
                       "link_expiry_min": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
                       "reset_link": forget_url_link }

        message = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[fpr.email],
            template_body=email_body,
            subtype=MessageType.html
          )
       
        template_name = "mail/password_reset.html"

        fm = FastMail(mail_conf)
        background_tasks.add_task(fm.send_message, message, template_name)'''
        background_tasks.add_task(send_email_reset_password, user.email, user.username, str(request.base_url))
        return JSONResponse(status_code=status.HTTP_200_OK,
           content={"message": "Email has been sent", "success": True,
               "status_code": status.HTTP_200_OK})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Something Unexpected, Server Error")