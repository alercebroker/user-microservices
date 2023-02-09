from pydantic import BaseModel, Field

class TokenIn(BaseModel):
    token: str = Field()

class RefreshIn(BaseModel):
    token: str = Field()
