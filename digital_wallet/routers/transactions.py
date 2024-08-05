from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..models import DBTransaction, Transaction, CreatedTransaction, UpdatedTransaction, engine

router = APIRouter(prefix="/transactions")

@router.post("")
async def create_transaction(transaction: CreatedTransaction) -> Transaction:
    data = transaction.dict()
    db_transaction = DBTransaction(**data)
    with Session(engine) as session:
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
    return Transaction.from_orm(db_transaction)

@router.get("/{transaction_id}")
async def read_transaction(transaction_id: int) -> Transaction:
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if db_transaction:
            return Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.put("/{transaction_id}")
async def update_transaction(transaction_id: int, transaction: UpdatedTransaction) -> Transaction:
    data = transaction.dict()
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        for key, value in data.items():
            setattr(db_transaction, key, value)
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
    return Transaction.from_orm(db_transaction)

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int) -> dict:
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if db_transaction:
            session.delete(db_transaction)
            session.commit()
            return {"message": "delete success"}
    raise HTTPException(status_code=404, detail="Transaction not found")
