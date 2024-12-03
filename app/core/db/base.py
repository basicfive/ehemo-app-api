from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import base_settings

engine = create_engine(
    base_settings.DATABASE_URL,
    pool_size=20,          # 기본 풀 크기
    max_overflow=20,       # 추가 허용 연결 수
    pool_timeout=60,       # 타임아웃 시간
    pool_pre_ping=True     # 연결 상태 확인
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
