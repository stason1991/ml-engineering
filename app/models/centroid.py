from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Centroid(Base):
    __tablename__ = "centroids"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_id: Mapped[int] = mapped_column(ForeignKey("ml_models.id"), nullable=False)
    model: Mapped["MLModel"] = relationship(back_populates="centroids")