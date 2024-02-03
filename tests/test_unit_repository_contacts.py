import unittest
from unittest.mock import AsyncMock, MagicMock

from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_contacts_by_birthday,
    create_contact,
    update_contact,
    delete_contact
)


class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=8, username='Test', password="qwerty!!", confirmation=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, 
                    f_name='Yarko', 
                    l_name='Durko', 
                    email='123@123.com',
                    phone='+380630000000',
                    birthday=date(2024, 2, 1),
                    created_at=date(2024, 2, 1),
                    updated_at=date(2024, 2, 1),
                    user_id=8,
                    user=self.user
                )]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)
    
    async def test_get_contacts_by_birthday(self):
        today = date.today()
        end_date = today + timedelta(days=7)
        contacts = [Contact(id=1, 
                    f_name='Yarko', 
                    l_name='Durko', 
                    email='123@123.com',
                    phone='+380630000000',
                    birthday=date(2024, 2, 1),
                    created_at=date(2024, 2, 1),
                    updated_at=date(2024, 2, 1),
                    user_id=8,
                    user=self.user
                )]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts_by_birthday(today, end_date, self.session, self.user)
        self.assertEqual(result, contacts)
        
        
    async def test_get_contact(self):
        contact = [Contact(id=1, 
                    f_name='', 
                    l_name='', 
                    email='',
                    phone='',
                    user_id=8,
                    user=self.user
                )]
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, contact)
        
    async def test_create_contact(self):
        body = ContactSchema(
            f_name="test22", 
            l_name="test2", 
            email="test@test.com", 
            phone="+380630000000", 
            birthday=date(2024, 2, 1), 
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.f_name, body.f_name)
        self.assertEqual(result.l_name, body.l_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
    
    async def test_update_contact(self):
        body = ContactUpdateSchema(
            f_name="test22", 
            l_name="test2", 
            email="test@test.com", 
            phone="+380630000000", 
            birthday=date(2024, 2, 1),
            completed=True 
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=2, 
            f_name="test22", 
            l_name="test2", 
            email="test@test.com", 
            phone="+380630000000", 
            birthday=date(2024, 2, 1),
            user=self.user
            )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(2, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.f_name, body.f_name)
        self.assertEqual(result.l_name, body.l_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        
    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=2, 
            f_name="test2", 
            l_name="test2", 
            email="test@test.com", 
            phone="+380630000000", 
            birthday=date(2024, 2, 1),
            user=self.user
            )
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(2, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)
if __name__ == '__main__':
    unittest.main()