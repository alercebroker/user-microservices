from pydantic import BaseModel, Field

class VerifyIn(BaseModel):
    token: str = Field()

class RefreshIn(BaseModel):
    token: str = Field()

class AuthToken(BaseModel):
    access: str = Field()
    refresh: str = Field()
