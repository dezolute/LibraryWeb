from sqladmin import ModelView


class BaseAdmin(ModelView):
    column_list = []
    pk_columns = ['id'] # type: ignore
    show_primary_keys = True
    column_sortable_list = column_list
    column_searchable_list = column_list