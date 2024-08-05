from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship

from . import items, wallets

class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    wallet_id: int
    amount: float

class CreatedTransaction(BaseTransaction):
    pass

class UpdatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int

class DBTransaction(Transaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="items.id")
    wallet_id: int = Field(foreign_key="wallets.id")
    amount: float = Field(default=0.0)

    item: Optional[items.DBItem] = Relationship(back_populates="transactions")
    wallet: Optional[wallets.DBWallet] = Relationship(back_populates="transactions")

#items.DBItem.transactions = Relationship(back_populates="item")
#wallets.DBWallet.transactions = Relationship(back_populates="wallet")
