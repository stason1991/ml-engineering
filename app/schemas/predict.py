from pydantic import BaseModel
from uuid import UUID

class PredictionRequest(BaseModel):
    model_id: int