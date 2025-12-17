from app.models.book_copy import BookCopyORM as BookCopie
from app.utils.admin.views.base import BaseAdmin


class BookCopyAdmin(BaseAdmin, model=BookCopie):
    column_list = [
        "serial_num",
        "book_id",
        "status",
        "access_type"
    ]