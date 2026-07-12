from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models import reconciliation  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy 모델들의 metadata를 Alembic에 알려준다.
# 이 값이 있어야 alembic revision --autogenerate가 모델 변경사항을 감지한다.
target_metadata = Base.metadata


# alembic.ini의 sqlalchemy.url 대신 .env의 DATABASE_URL을 사용한다.
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """오프라인 모드에서 migration을 실행한다."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드에서 DB에 연결해 migration을 실행한다."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()