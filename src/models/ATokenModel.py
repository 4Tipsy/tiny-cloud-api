
from pydantic import BaseModel




class ATokenModel(BaseModel):
    
  user_id: int
  jwt_epoch: int