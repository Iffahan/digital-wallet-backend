from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, ConfigDict
import pydantic
from datetime import datetime

from . import transactions

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    balance: float = pydantic.Field(default=0.0, example=100.0)

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int

class DBWallet(BaseWallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)
    last_updated: datetime = Field(default=datetime.utcnow(), sa_column_kwargs={"onupdate": datetime.utcnow})

    user_id: int = Field(default=None, foreign_key="users.id")
    user: Optional["DBUser"] = Relationship(back_populates="wallet")  # Use a string to reference the class
    
    transactions: list["DBTransaction"] = Relationship(back_populates="wallet")


class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int
