from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

from datetime import date
import datetime



async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the given user.
    
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

#_____________11.12 _________________A&A__________________________________
async def get_all_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_all_contacts function returns all contacts for a given user.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Determine how many contacts to skip before returning the results
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Identify the user who is making the request
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact object from the database.
    
    :param contact_id: int: Filter the contact by id
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Check if the user is allowed to access the contact
    :return: A contact object, not a list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()

async def get_contacts_by_birthday(today: date, end_date: date, db: AsyncSession, user: User):
    """
    The get_contacts_by_birthday function returns a list of contacts that have birthdays between the start and end dates.
        
    
    :param today: date: Set the date range for the query
    :param end_date: date: Specify the end date of the range
    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    try:
        date_range_filter = and_(Contact.birthday >= today, Contact.birthday <= end_date)
        stmt = select(Contact).filter(date_range_filter)
        contacts = await db.execute(stmt)
        return contacts.scalars().all()
    except Exception as e:
        print(f"Error: {e}")
        return []

async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user object from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)  # (title=body.title, description=body.description)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.
    
    :param contact_id: int: Specify the contact that will be updated
    :param body: ContactUpdateSchema: Pass in the updated contact information
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure that the user is only updating their own contacts
    :return: The updated contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.f_name = body.f_name
        contact.l_name = body.l_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass in the database session
    :param user: User: Check if the user is authorized to delete the contact
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact