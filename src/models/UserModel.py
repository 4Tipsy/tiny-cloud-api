
from pydantic import BaseModel
from typing import Literal, List




class SharedDictModel(BaseModel):
  """_part of UserModel"""
  hashed_link: str
  base_type: Literal["folder", "file"]
  file_field: Literal["mere", "special", "temporary"]
  abs_path_to_entity: str




class UserModel(BaseModel):

  verified: bool
  jwt_epoch: int

  user_id: int  
  user_name: str
  user_img: str

  user_email: str
  hashed_password: str

  shared: List[SharedDictModel]


  used_space: float
  available_space: float





class UserInRespModel(BaseModel):

  verified: bool

  user_id: int  
  user_name: str

  user_email: str

  shared: List[SharedDictModel]

  used_space: float
  available_space: float