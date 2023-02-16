from pydantic import BaseModel, Field

class NewUserIn(BaseModel):
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    username: str = Field()
    password: str = Field()

class LoginIn(BaseModel):
    username: str = Field()
    password: str = Field()
