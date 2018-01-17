"""SQLAlchemy Metadata and Session object"""
from typing import Callable
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session

# SQLAlchemy database engine.  Updated by model.init_model()
engine: Engine = None

# SQLAlchemy session manager.  Updated by model.init_model()
Session: Callable[..., Session] = None

# Global metadata. If you have multiple databases with overlapping table
# names, you'll need a metadata for each database
metadata = MetaData()