from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    balance: float = 0.0

class CreatedWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int

class DBWallet(Wallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, index=True)
    balance: float = Field(default=0.0)
