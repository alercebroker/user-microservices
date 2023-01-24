from pydantic import BaseModel, Field

class LoginIn(BaseModel):
    code: str = Field()
    state: str = Field()
