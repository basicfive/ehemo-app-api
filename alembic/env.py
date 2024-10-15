import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.db import Base
from app.models import hair, generation, scene, image, user, base

# Alembic Config 객체 생성
config = context.config

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL 설정
config.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL'))

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData 객체 추가 - 이 부분이 중요합니다
target_metadata = Base.metadata

# run_migrations_offline() 및 run_migrations_online() 함수를 여기에 추가하세요
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()