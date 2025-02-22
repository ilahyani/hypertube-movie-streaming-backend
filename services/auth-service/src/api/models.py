from pydantic import BaseModel, EmailStr, Field

class UserRegistrationModel(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=3, max_length=16, pattern=r'^[a-zA-Z0-9]+$')
    last_name: str = Field(..., min_length=3, max_length=16, pattern=r'^[a-zA-Z0-9]+$')
    username: str = Field(..., min_length=3, max_length=16, pattern=r'^[a-zA-Z0-9]+$')
    passwd: str = Field(min_length=8, max_length=16)
    picture: str

class UserLoginModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=16, pattern=r'^[a-zA-Z0-9]+$')
    password: str = Field(..., min_length=8, max_length=16)