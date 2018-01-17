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


def create_config(alembic_repository:str, sqlalchemy_url:str) -> Config:
    """
    Create the Alembic Config object based on the application configuration.

    :rtype: :class:`alembic.config.Config`
    """
    if not os.path.isdir(alembic_repository):
        raise RuntimeError('The alembic.script_location path {} does not exist.'.format(alembic_repository))
    elif not os.path.isfile(os.path.join(alembic_repository, 'env.py')):
        raise RuntimeError('The alembic.script_location path {} does not look like a migrations directory. '
                           '(no env.py file)'.format(alembic_repository))

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', alembic_repository)
    alembic_cfg.set_main_option('sqlalchemy.url', sqlalchemy_url)

    return alembic_cfg


def get_database_version():
    """
    Gets the current database revision (partial GUID).
    :rtype: str
    """
    context = MigrationContext.configure(meta.engine)
    return context.get_current_revision()


def get_head_version():
    """
    Gets the latest model revision available (partial GUID).
    :rtype: str
    """
    alembic_cfg = create_config()
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()
