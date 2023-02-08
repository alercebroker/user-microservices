from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field
    first_name: str = Field()
    last_name: str = Field()
    institution: str = Field()