import unittest
from datetime import timedelta

import jwt

from app.models import UserORM
from app.repositories import UserRepository, AbstractRepository
from app.utils import OAuth2Utility
from app.config import auth_config

async def add_user():
    user_repo: AbstractRepository = UserRepository()
    data = {
        "email": "dezo@example.com",
        "name": "John Caminskiy",
        "encrypted_password": "123",
    }
    db_user: UserORM = await user_repo.create(data)
    try:
        yield db_user
    finally:
        await user_repo.delete(id=db_user.id)


class TestOauth2Utility(unittest.TestCase):
    def test_get_hashed_password(self):
        hashed = OAuth2Utility.get_hashed_password("")
        self.assertIsNotNone(hashed)

    def test_verify_password(self):
        hashed = OAuth2Utility.get_hashed_password("123")
        is_veryfi = OAuth2Utility.verify_password('123', hashed)
        self.assertTrue(is_veryfi)

    def test_create_access_token(self):
        data = {
            "sub": "123@example.com",
            "name": "John Caminskiy"
        }
        token = OAuth2Utility.create_access_token(data, expires_delta=timedelta(minutes=15))
        payload = jwt.decode(token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALGORITHM])
        self.assertEqual(payload["sub"], "123@example.com")
        self.assertEqual(payload["name"], "John Caminskiy")

    async def test_get_current_user(self):
        async with add_user() as db_user:
            data = {
                "sub": db_user.email,
                "name": db_user.name
            }

            token = OAuth2Utility.create_access_token(data, expires_delta=timedelta(minutes=15))
            user_dto = await OAuth2Utility.get_current_user(token)
            self.assertIsNotNone(user_dto)
            self.assertEqual(user_dto.id, db_user.id)

if __name__ == '__main__':
    unittest.main()
