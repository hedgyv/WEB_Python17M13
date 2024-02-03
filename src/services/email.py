from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import config

#__________________1.13.Email_______________________________________________________________________________________
# conf = ConnectionConfig(
#     MAIL_USERNAME="hedgy85@meta.ua",
#     MAIL_PASSWORD="qwe123!!Yarko",
#     MAIL_FROM="hedgy85@meta.ua",
#     MAIL_PORT=465,
#     MAIL_SERVER="smtp.meta.ua",
#     MAIL_FROM_NAME="Contact Systems",
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
#     TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
# )

    #__________________2.13.Env_______________________________________________________________________________________
conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Contact Systems",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)
    #__________________2.13.Env_______________________________________________________________________________________|

async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify their email address.
        The function takes in three arguments:
            -email: the user's email address, which is used as a unique identifier for them.
            -username: the username of the user, which is displayed in the body of the message.
            -host: this is used to construct a URL that will be sent in an HTML template.
    
    :param email: EmailStr: Ensure that the email is a valid email address
    :param username: str: Pass the username of the user to be used in the email template
    :param host: str: Pass the hostname of the server to the template
    :return: None
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
        
        
async def send_email_reset_password(email: EmailStr, username: str, host: str): 
    """
    The send_email_reset_password function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The user's username.
            host (str): The hostname of the server where this function is being called from.
    
    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username of the user to be reset
    :param host: str: Pass the hostname of the server to be used in the link
    :return: Nothing
    :doc-author: Trelent
    """
    try: 
        token_verification = auth_service.create_email_token({"sub": email}) 
        message = MessageSchema( 
            subject="Test ", 
            recipients=[email], 
            template_body={"host": host, "username": username, "token": token_verification}, 
            subtype=MessageType.html 
        ) 
 
        fm = FastMail(conf) 
        await fm.send_message(message, template_name="reset_password.html") 
    except ConnectionErrors as err: 
        print(err)
        
