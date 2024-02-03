from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User #8.12__A&A__приутствие аутентификации
from src.services.auth import auth_service #8.12__A&A__приутствие аутентификации
from src.database.db import get_db
from src.repository import contacts as reps_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse

import re
from datetime import date, timedelta

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The get_contacts function returns a list of contacts.
        The limit and offset parameters are used to paginate the results.
        
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify that the limit must be greater than or equal to 10
    :param le: Specify the maximum value that can be passed in
    :param offset: int: Specify the offset in the database
    :param ge: Specify that the limit must be greater than or equal to 10
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await reps_contacts.get_contacts(limit, offset, db, user)
    return contacts

#_____________11.12 _________________A&A__________________________________
@router.get("/all", response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The get_contacts function returns a list of contacts.
        The limit and offset parameters are used to paginate the results.
        
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify that the limit must be greater than or equal to 10
    :param le: Limit the maximum number of contacts returned
    :param offset: int: Specify the number of contacts to skip
    :param ge: Specify that the limit must be greater than or equal to 10
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the auth_service
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await reps_contacts.get_all_contacts(limit, offset, db, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The get_contact function returns a contact by its ID.
        If the contact does not exist, it raises an HTTP 404 error.
    
    
    :param contact_id: int: Specify the path parameter
    :param db: AsyncSession: Get a database connection
    :param user: User: Get the current user
    :return: A contact
    :doc-author: Trelent
    """
    contact = await reps_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact

@router.get("/birthdays/", response_model=list[ContactResponse])
async def get_contact_by_bday(
    days_ahead: int = Query(7, description="Number of days ahead to search for birthdays"),
    db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The get_contact_by_bday function returns a list of contacts whose birthdays fall within the specified number of days ahead.
        The default is 7 days, but this can be changed by passing in an integer value for the 'days_ahead' parameter.
    
    
    :param days_ahead: int: Specify the number of days ahead to search for birthdays
    :param description: Document the api
    :param db: AsyncSession: Pass in the database session
    :param user: User: Get the user from the request
    :return: A list of contacts
    :doc-author: Trelent
    """
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    contacts = await reps_contacts.get_contacts_by_birthday(today, end_date, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The create_contact function creates a new contact in the database.
        It takes a ContactSchema object as input, and returns the newly created contact.
    
    
    :param body: ContactSchema: Validate the request body and deserialize it into a contact object
    :param db: AsyncSession: Get the database connection
    :param user: User: Get the current user
    :return: The contact that was created
    :doc-author: Trelent
    """
    if not re.match(r'^[\d\+\(\)]+$', body.phone):
        raise HTTPException(status_code=422, detail="Input valid phone")
    contact = await reps_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The update_contact function updates a contact in the database.
        It takes an id, and a body containing the fields to update.
        The function returns the updated contact.
    
    :param body: ContactUpdateSchema: Validate the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await reps_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), 
                    user: User = Depends(auth_service.get_current_user) #8.12__A&A__User=__приутствие аутентификации
                    ):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): A connection to the database.
        Returns:
            dict: A dictionary containing information about whether or not 
                deleting was successful and, if so, which user was deleted.
    
    :param contact_id: int: Specify the path parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the user that is currently logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await reps_contacts.delete_contact(contact_id, db, user)
    return contact