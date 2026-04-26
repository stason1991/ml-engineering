from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
  from app.models.centroid import Centroid

class MLModel(Base):
    """Таблица ML-моделей"""
    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Поле для определения типа алгоритма (K-Means, LogReg и т.д.)
    model_type: Mapped[str] = mapped_column(String(50))

    # Связь с центроидами (эталонами)
    centroids: Mapped[List["Centroid"]] = relationship(
    back_populates="model", 
    cascade="all, delete-orphan",
    lazy="selectin"  # Подгружаем центроиды сразу, чтобы они были доступны для предикта
    )

    __mapper_args__ = {
      "polymorphic_on": "model_type",
      "polymorphic_identity": "base_model",
    }

    def predict(self, data_vector: List[float]) -> str:
        """Интерфейс для предсказания"""
        raise NotImplementedError


class EuclideanKMeansModel(MLModel):
    """Реализация модели на основе Евклидова расстояния"""
    __mapper_args__ = {
      "polymorphic_identity": "kmeans_euclidean",
    }

    def predict(self, data_vector: List[float]) -> str:
      if not self.centroids:
        return "Ошибка: У модели нет настроенных центроидов"
        
        # Здесь будет поиск центроида с минимальным расстоянием до data_vector
      return f"Результат кластеризации от {self.name}"