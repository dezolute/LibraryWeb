from app.models.profile import ProfileORM as Profile
from app.utils.admin.views.base import BaseAdmin


class ProfileAdmin(BaseAdmin, model=Profile):
    column_list = [
        'id',
        'full_name',
        'avatar_url'
    ]