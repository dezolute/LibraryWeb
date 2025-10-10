from sqladmin import ModelView, Admin
from fastapi import FastAPI

from app.models import BookORM, UserORM, RequestORM
from app.config.database import db


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

class RequestAdmin(BaseAdmin, model=RequestORM):
    column_list = [
        'id',
        'user_id',
        'book_id',
        'status',
        'created_at',
        'updated_at',
    ]
    column_details_exclude_list = [
        'user',
        'book'
    ]

def get_admin(app: FastAPI) -> Admin:


    admin = Admin(
        app=app,
        engine=db.engine,
        session_maker=db.session_factory,
    )

    admin.add_view(UserAdmin)
    admin.add_view(BookAdmin)
    admin.add_view(RequestAdmin)

    return admin