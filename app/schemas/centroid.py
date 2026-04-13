from pydantic import BaseModel, Field

class CentroidBase(BaseModel):
    name: str = Field(..., description="Название центроида")
    model_id: int = Field(..., description="ID связанной ML модели")

class CentroidCreate(CentroidBase):
    pass

class CentroidResponse(CentroidBase):
    id: int

    class Config:
        from_attributes = True