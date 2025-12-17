from app.models.reader import ReaderORM
from app.utils.admin.views.base import BaseAdmin


class ReaderAdmin(BaseAdmin, model=ReaderORM):
    column_list = [
        'id',
        'name',
        'email',
        'role',
        'verified',
    ]
    column_details_exclude_list = [
        'encrypted_password',
        'requests'
    ]