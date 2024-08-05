from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..models import DBWallet, Wallet, CreatedWallet, UpdatedWallet, engine

router = APIRouter(prefix="/wallets")

@router.post("")
async def create_wallet(wallet: CreatedWallet) -> Wallet:
    data = wallet.dict()
    db_wallet = DBWallet(**data)
    with Session(engine) as session:
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.get("/{user_id}")
async def read_wallet(user_id: int) -> Wallet:
    with Session(engine) as session:
        db_wallet = session.exec(select(DBWallet).where(DBWallet.user_id == user_id)).first()
        if db_wallet:
            return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/{user_id}")
async def update_wallet(user_id: int, wallet: UpdatedWallet) -> Wallet:
    data = wallet.dict()
    with Session(engine) as session:
        db_wallet = session.exec(select(DBWallet).where(DBWallet.user_id == user_id)).first()
        if not db_wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        for key, value in data.items():
            setattr(db_wallet, key, value)
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/{user_id}")
async def delete_wallet(user_id: int) -> dict:
    with Session(engine) as session:
        db_wallet = session.exec(select(DBWallet).where(DBWallet.user_id == user_id)).first()
        if db_wallet:
            session.delete(db_wallet)
            session.commit()
            return {"message": "delete success"}
    raise HTTPException(status_code=404, detail="Wallet not found")
