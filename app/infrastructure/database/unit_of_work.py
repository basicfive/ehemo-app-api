from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db.base import get_db

class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db

    def begin(self):
        # 트랜잭션 시작 로직
        pass

    def commit(self):
        self.db.commit()
        # refresh 로직
        for obj in self.db.new:
            self.db.refresh(obj)
        for obj in self.db.dirty:
            self.db.refresh(obj)

    def rollback(self):
        self.db.rollback()

def get_unit_of_work(db: Session = Depends(get_db)):
    return UnitOfWork(db)

