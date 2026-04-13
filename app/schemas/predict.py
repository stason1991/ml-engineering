from pydantic import BaseModel
from uuid import UUID

class PredictionRequest(BaseModel):
    user_id: UUID
    model_id: int