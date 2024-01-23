
from pydantic import BaseModel





class UserModel(BaseModel):

  verified: bool
  jwt_epoch: int

  user_id: int  
  user_name: str
  user_img: str

  user_email: str
  hashed_password: str


  used_space: float
  available_space: float
