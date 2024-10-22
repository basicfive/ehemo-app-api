from sqlalchemy import Column, String, Integer

from app.core.db.time_stamp_model import TimeStampModel

class User(TimeStampModel):
    __tablename__ = "user"
    email = Column(String(50), nullable=False, index=True)
    token = Column(Integer, default=0, nullable=False)

    def has_enough_token(self) -> bool:
        if self.token == 0:
            return False
        return True


