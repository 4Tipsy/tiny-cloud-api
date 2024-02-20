
from fastapi import Request, HTTPException, status
from jwt.exceptions import InvalidTokenError
import jwt
from typing import Tuple


# modules
from src.cfg import Cfg
from src.controllers.DbController import DbController, DbNotFoundException
from src.models.ATokenModel import ATokenModel
from src.models.UserModel import UserModel








def auth(request: Request) -> int | HTTPException:
  """Takes jwt from cookies and tries to decode it. If ok returns user_id(contains in jwt) | Will raise HTTPException if user is not verified"""

  user_id, user_is_verified = _auth(request)
  if not user_is_verified:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")
  
  return user_id


def auth_with_unverified_user_allowed(request: Request) -> int | HTTPException:
  """Takes jwt from cookies and tries to decode it. If ok returns user_id(contains in jwt) | Will NOT raise HTTPException if user is not verified"""
  
  user_id, user_is_verified = _auth(request)
  return user_id










def _auth(request: Request) -> Tuple[int, bool] | HTTPException:
  """Takes jwt from cookies and tries to decode it. If ok returns user_id(contains in jwt)"""



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
  try:
    current_user = DbController.get_user_by_id(a_token.user_id)
  except DbNotFoundException:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')

  if current_user.jwt_epoch != a_token.jwt_epoch:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')
  
  

  # if everything is ok
  return (a_token.user_id, current_user.verified)