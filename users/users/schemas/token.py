from pydantic import BaseModel, Field

class AuthToken(BaseModel):
    access: str = Field()
    refresh: str = Field()
