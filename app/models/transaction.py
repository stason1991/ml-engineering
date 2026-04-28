from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Float, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.wallet import Wallet

class Transaction(Base):
    """Базовая модель транзакций"""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[UUID] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(20))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "transaction",
    }

    def apply(self, wallet: "Wallet"):
        pass


class DebitTransaction(Transaction):
    """Списание средств"""
    __mapper_args__ = {
        "polymorphic_identity": "debit",
    }

    def apply(self, wallet: "Wallet"):
        if wallet.balance < self.amount:
            raise ValueError("Недостаточно средств")
        wallet.balance -= self.amount


class CreditTransaction(Transaction):
    """Пополнение баланса"""
    __mapper_args__ = {
        "polymorphic_identity": "credit",
    }

    def apply(self, wallet: "Wallet"):
        wallet.balance += self.amount