import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Tambahkan path project agar bisa import dengan benar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import settings dari config.py kamu
from app.core.config import settings  # sesuaikan jika path config-mu beda
from app.core.database import Base
from app import models  # pastikan ini load semua model

# Alembic config
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject DATABASE_URL dari settings ke Alembic config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Target metadata (untuk autogenerate migration)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
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
