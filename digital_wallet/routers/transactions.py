from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from datetime import datetime

from .. import models, deps

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=models.DBTransaction)
async def create_transaction(
    item_id: int,
    amount: int,  # Represents the number of items being purchased
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.DBTransaction:
    # Fetch the user's wallet
    user_wallet = await session.exec(
        select(models.DBWallet).where(models.DBWallet.user_id == current_user.id)
    )
    wallet = user_wallet.first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Fetch the item to ensure it exists
    item = await session.get(models.DBItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Calculate total cost
    total_cost = item.price * amount
    
    # Ensure the wallet has sufficient balance
    if wallet.balance < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Create the transaction
    transaction = models.DBTransaction(
        user_id=current_user.id,
        item_id=item_id,
        wallet_id=wallet.id,
        amount=total_cost,  # Store the total cost in the transaction
        timestamp=datetime.utcnow()
    )
    
    # Update the wallet balance by subtracting the total cost
    wallet.balance -= total_cost
    session.add(wallet)
    
    # Save the transaction
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    return transaction


@router.get("", response_model=models.TransactionList)
async def read_transactions(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.TransactionList:
    SIZE_PER_PAGE = 50
    
    result = await session.exec(
        select(models.DBTransaction).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    transactions = result.all()

    total_transactions = await session.exec(select(func.count(models.DBTransaction.id)))
    page_count = (total_transactions.first() + SIZE_PER_PAGE - 1) // SIZE_PER_PAGE

    return models.TransactionList(
        transactions=transactions,
        page=page,
        page_count=page_count,
        size_per_page=SIZE_PER_PAGE
    )


@router.get("/{transaction_id}", response_model=models.DBTransaction)
async def read_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.DBTransaction:
    transaction = await session.get(models.DBTransaction, transaction_id)
    if transaction:
        return transaction
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
