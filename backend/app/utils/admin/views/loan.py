from app.models.loan import LoanORM as Loan
from app.utils.admin.views.base import BaseAdmin

class LoanAdmin(BaseAdmin, model=Loan):
    column_list = [
        'id',
        'reader_id',
        'copy_id',
        'issue_date',
        'due_date',
        'return_date'
    ]