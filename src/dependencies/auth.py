
from fastapi import Request, HTTPException, status
from jwt.exceptions import InvalidTokenError
import jwt



# modules
from src.cfg import Cfg
from src.controllers.DbController import DbController
from src.models.ATokenModel import ATokenModel
from src.models.UserModel import UserModel





def auth(request: Request) -> int | HTTPException:
  """Takes jwt from cookies and tries to decode it. If ok returns user_id(decoded in jwt)"""



  a_token: str = request.cookies.get("a-token")

  # if no token
  if not a_token:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not logged')




  # decode
  try:
    a_token = jwt.decode(a_token, Cfg.main_app.jwt_secret, algorithms=["HS256"])
    a_token: ATokenModel = ATokenModel(**a_token)

  except InvalidTokenError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')
  


  # authenticate
  current_user = DbController.get_user_by_id(a_token.user_id)

  if current_user.jwt_epoch != a_token.jwt_epoch:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')
  
  if not current_user.verified:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")
  

  # if everything is ok
  return a_token.user_id