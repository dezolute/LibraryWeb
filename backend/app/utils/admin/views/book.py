from app.models.book import BookORM as Book
from app.utils.admin.views.base import BaseAdmin


class BookAdmin(BaseAdmin, model=Book):
    
    column_list = [
        'id',
        'title',
        'author',
        'year_publication',
    ]

    column_details_exclude_list = ['requests']