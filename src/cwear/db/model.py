from sqlalchemy import Integer, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
import os

DB = os.environ.get('DATABASE_URL')
if not DB:
    DB = "postgresql+psycopg2://cwear:cwear@localhost/cwear"

DBModelBase = declarative_base()


class DatabaseManager(object):

    def __init__(self):
        self._db_engine = None
        self._scoped_session = None
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        self._db_engine = create_engine(DB)
        self._db_engine.connect()
        self._scoped_session = scoped_session(sessionmaker(self._db_engine))

    def get_db_session(self):
        return self._scoped_session()


class User(DBModelBase):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    password = Column(String)
    admin = Column(Boolean, default=False)
