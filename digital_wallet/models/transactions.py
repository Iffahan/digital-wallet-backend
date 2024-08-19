from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional

class DBTransaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    item_id: int = Field(foreign_key="items.id")
    wallet_id: int = Field(foreign_key="wallets.id")
    amount: float
    timestamp: datetime = Field(default=datetime.utcnow())

    user: Optional["DBUser"] = Relationship(back_populates="transactions")
    item: Optional["DBItem"] = Relationship(back_populates="transactions")
    wallet: Optional["DBWallet"] = Relationship(back_populates="transactions")

class TransactionList(SQLModel):
    transactions: list[DBTransaction]
    page: int
    page_count: int
    size_per_page: int
