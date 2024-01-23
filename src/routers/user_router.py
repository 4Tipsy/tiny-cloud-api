
from fastapi import APIRouter, Depends, File, UploadFile, Response, HTTPException, status
from pydantic import BaseModel
from typing import Literal
import datetime


# modules
from src.dependencies.auth import auth
from src.models.UserModel import UserModel
from src.controllers.UserController import UserController
from src.controllers.DbController import DbController, DbNotFoundException





router = APIRouter(prefix="/api/user-service", tags=["User service"])

class _BaseRes(BaseModel):
  result: Literal["success"]










class _LoginReq(BaseModel):
  user_email: str
  password: str

# router function
@router.post("/login")
def handle_login(request: _LoginReq, response: Response) -> _BaseRes:

  a_token = UserController.get_a_token(request.user_email, request.password)

  # get current_time + 30days to pass in cookie expires
  expires_time = datetime.datetime.utcnow() + datetime.timedelta(days=30)
  expires_time = expires_time.strftime('%a, %d %b %Y %H:%M:%S GMT')


  response.set_cookie(key='a-token', value=a_token, expires=expires_time)
  return {'result': 'success'}





class _RegisterReq(BaseModel):
  user_email: str
  password: str
  user_name: str

# router function
@router.post("/register")
def handle_register(request: _RegisterReq) -> _BaseRes:

  UserController.create_new_user(request.user_email, request.password, request.user_name)

  return {'result': 'success'}







class _GetCurrentUserRes(BaseModel):
  result: Literal["success"]
  user: UserModel

# router function
@router.get("/get-current-user", description="**(Auth needed)**")
def handle_get_current_user(user_id=Depends(auth)) -> _GetCurrentUserRes:

  try:
    user = DbController.get_user_by_id(user_id)
  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')
  
  return {
    "result": "success",
    "user": user
  }