from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select

from . import merchants, items, wallets, transactions

from .items import *
from .merchants import *
from .wallets import *
from .transactions import * 


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://admin:admin@localhost/db_wallet",
    echo=True,
    connect_args=connect_args,
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session