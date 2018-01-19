"""
Various utility functions.
"""
from __future__ import absolute_import
import os.path
import string

import alembic

from alembic.runtime.migration import MigrationContext
from alembic.context import EnvironmentContext
from alembic.config import Config
from alembic.script import ScriptDirectory

from . import meta


def create_config(sqlalchemy_url:str) -> Config:
    """
    Create the Alembic Config object based on the application configuration.

    :rtype: :class:`alembic.config.Config`
    """
    alembic_repository = 'freezing.model:migrations'

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', alembic_repository)
    alembic_cfg.set_main_option('sqlalchemy.url', sqlalchemy_url)

    return alembic_cfg


def get_database_version() -> str:
    """
    Gets the current database revision (partial GUID).
    """
    context = MigrationContext.configure(meta.engine)
    return context.get_current_revision()
