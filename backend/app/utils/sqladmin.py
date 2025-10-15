from fastapi import FastAPI
from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.config import auth_config
from app.config.database import db
from app.models import BookORM, UserORM, RequestORM
from app.models.types import Role
from app.repositories import UserRepository, AbstractRepository
from app.utils import OAuth2Utility


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str) -> None:
        self.user_repository: AbstractRepository = UserRepository()
        super().__init__(secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        db_user = await self.user_repository.find(email=email)
        if not db_user:
            return False
        if db_user.role != Role.ADMIN:
            return False

        try:
            return OAuth2Utility.verify_password(password, db_user.encrypted_password)
        finally:
            request.session.update({
                "access_token": OAuth2Utility.get_tokens({
                    'sub': db_user.email,
                    'name': db_user.name,
                }).access_token,
            })

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("access_token")

        if not token:
            return False

        return True


class BaseAdmin(ModelView):
    column_list = []
    pk_columns = ['id']
    show_primary_keys = True
    column_sortable_list = column_list
    column_searchable_list = column_list


class UserAdmin(BaseAdmin, model=UserORM):
    column_list = [
        'id',
        'name',
        'email',
        'role',
        'verified',
        'created_at',
    ]
    column_details_exclude_list = [
        'encrypted_password',
        'requests'
    ]


class BookAdmin(BaseAdmin, model=BookORM):
    column_list = [
        'id',
        'title',
        'author',
        'priority',
        'count',
        'year_publication'
    ]

    column_details_exclude_list = ['requests']

class RequestAdmin(BaseAdmin, model=RequestORM):
    column_list = [
        'id',
        'user_id',
        'book_id',
        'status',
        'created_at',
        'updated_at',
    ]


def get_admin(app: FastAPI) -> Admin:
    backend_auth = AdminAuth(auth_config.JWT_SECRET)

    admin = Admin(
        app=app,
        engine=db.engine,
        session_maker=db.session_factory,
        authentication_backend=backend_auth,
        favicon_url="/LibraryWeb.svg",
    )

    admin.add_view(UserAdmin)
    admin.add_view(BookAdmin)
    admin.add_view(RequestAdmin)

    return admin
