from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from .. import models, deps

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.post("", response_model=models.Wallet)
async def create_wallet(
    wallet: models.CreatedWallet,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Wallet:
    # Check if the user already has a wallet
    existing_wallet = await session.exec(
        select(models.DBWallet).where(models.DBWallet.user_id == current_user.id)
    )
    if existing_wallet.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a wallet"
        )
    
    db_wallet = models.DBWallet(user_id=current_user.id, **wallet.dict())
    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)
    return models.Wallet.from_orm(db_wallet)


@router.get("", response_model=models.WalletList)
async def read_wallets(
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.WalletList:
    result = await session.exec(select(models.DBWallet))
    wallets = result.all()

    return models.WalletList.from_orm(
        dict(wallets=wallets, page_size=0, page=0, size_per_page=0)
    )


@router.get("/{wallet_id}", response_model=models.Wallet)
async def read_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Wallet:
    db_wallet = await session.get(models.DBWallet, wallet_id)
    if db_wallet:
        return models.Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")


@router.put("/{wallet_id}", response_model=models.Wallet)
async def update_wallet(
    wallet_id: int,
    wallet: models.UpdatedWallet,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Wallet:
    db_wallet = await session.get(models.DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    if db_wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this wallet")

    # Update the wallet fields
    for key, value in wallet.dict(exclude_unset=True).items():
        setattr(db_wallet, key, value)

    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)

    return models.Wallet.from_orm(db_wallet)


@router.delete("/{wallet_id}", response_model=dict)
async def delete_wallet(
    wallet_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_wallet = await session.get(models.DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    if db_wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this wallet")

    await session.delete(db_wallet)
    await session.commit()

    return dict(message="Wallet deleted successfully")
