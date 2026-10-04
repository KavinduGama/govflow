from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import os
from dotenv import load_dotenv

# 1. Import our Base and models
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Load environment variables and override the sqlalchemy.url
load_dotenv()
database_url = os.getenv("DATABASE_URL", "postgresql://govflow:govflow_secret@localhost:5460/govflow_dev")
config.set_main_option("sqlalchemy.url", database_url)

# 3. Tell Alembic to look at our Base metadata to generate tables
target_metadata = Base.metadata

# Tables owned by LangGraph's PostgresSaver (created by checkpointer.setup(), not by our models).
# Without this, autogenerate would emit migrations that DROP them and wipe chat memory.
LANGGRAPH_TABLES = {"checkpoints", "checkpoint_blobs", "checkpoint_writes", "checkpoint_migrations"}

def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table" and name in LANGGRAPH_TABLES:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
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
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
