from sqlalchemy import Integer, Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, relationship
from sqlalchemy.orm.session import sessionmaker
import os

DB_URI = os.environ.get('DATABASE_URL')
if not DB_URI:
    DB_URI = "postgresql+psycopg2://cwear:cwear@localhost/cwear"

DBModelBase = declarative_base()


class DatabaseManager(object):

    def __init__(self):
        self._db_engine = None
        self._scoped_session = None
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        self._db_engine = create_engine(DB_URI)
        self._db_engine.connect()
        self._scoped_session = scoped_session(sessionmaker(self._db_engine))

    def get_db_session(self):
        return self._scoped_session()


class User(DBModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    password = Column(String)
    admin = Column(Boolean, default=False)


class SyncState(DBModelBase):
    __tablename__ = "syncstate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String)
    hapiaccount_id = Column(Integer, ForeignKey("hapiaccount.id"))
    last_sync_time = Column(DateTime)


class DeviceCloudAccount(DBModelBase):
    __tablename__ = "dcaccount"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)


class HumanApiAccount(DBModelBase):
    __tablename__ = "hapiaccount"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_key = Column(String)
    client_id = Column(String)


class CwearApplication(DBModelBase):
    __tablename__ = "cwearapplication"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    dcaccount = Column(Integer, ForeignKey("dcaccount.id"))
    hapiaccount = Column(Integer, ForeignKey("hapiaccount.id"))
    last_sync_time = Column(DateTime)
    sync_freq_secs = Column(Integer, default=60)
    related_dcaccount = relationship("DeviceCloudAccount")
    related_hapiaccount = relationship("HumanApiAccount")
