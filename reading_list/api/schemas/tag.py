from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(...)


class TagOut(BaseModel):
    id: int
    user_id: int
    name: str

    model_config = {
        'from_attributes': True
    }
