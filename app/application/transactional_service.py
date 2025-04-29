from app.infrastructure.database.unit_of_work import UnitOfWork

class TransactionalService:
    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work