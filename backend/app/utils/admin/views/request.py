from app.models.request import RequestORM
from app.utils.admin.views.base import BaseAdmin


class RequestAdmin(BaseAdmin, model=RequestORM):
    column_list = [
        'id',
        'reader_id',
        'book_id',
        'status',
        'created_at',
    ]