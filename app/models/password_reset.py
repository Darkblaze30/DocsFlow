from pydantic import BaseModel
from typing import Optional

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
class User(BaseModel):
    id: int
    email: str
    password: Optional[str] = None
    rol: str