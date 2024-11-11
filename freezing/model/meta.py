"""SQLAlchemy Metadata and Session object"""

import contextlib
from typing import Callable, ContextManager
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# SQLAlchemy database engine.  Updated by model.init_model()
engine: Engine = None

# SQLAlchemy session manager.  Updated by model.init_model()
scoped_session: Callable[..., Session] = None

# Global metadata. If you have multiple databases with overlapping table
# names, you'll need a metadata for each database
metadata = MetaData()


@contextlib.contextmanager
def transaction_context(read_only: bool = False) -> ContextManager[Session]:
    session = scoped_session()
    try:
        yield session
    except:
        session.rollback()
        raise
    else:
        if read_only:
            session.rollback()
        else:
            session.commit()
    finally:
        session.close()
