
from fastapi import APIRouter, Depends, File, UploadFile, Response, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal
import datetime, os


# modules
from src.dependencies.auth import auth, auth_with_unverified_user_allowed
from src.models.UserModel import UserModel, UserInRespModel
from src.controllers.UserController import UserController
from src.controllers.DbController import DbController, DbNotFoundException
from src.utils.validate_email import validate_email
from src.cfg import Cfg



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

  if not validate_email(request.user_email):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'"{request.user_email}" is not valid email address')
  
  # if ok
  UserController.create_new_user(request.user_email, request.password, request.user_name)

  return {'result': 'success'}







class _GetCurrentUserRes(BaseModel):
  result: Literal["success"]
  user: UserInRespModel

# router function
@router.get("/get-current-user", description="**(Auth needed)**")
def handle_get_current_user(user_id = Depends(auth_with_unverified_user_allowed)) -> _GetCurrentUserRes:
  
  try:
    user = DbController.get_user_by_id(user_id)
    user = UserInRespModel( **user.model_dump() )
  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')
  
  return {
    "result": "success",
    "user": user.model_dump()
  }





@router.get("/get-user-img", description="**(Auth needed)**")
def handle_get_user_img(user_id = Depends(auth_with_unverified_user_allowed)) -> FileResponse:
  try:
    user = DbController.get_user_by_id(user_id)
    user = UserModel( **user.model_dump() )
    path_to_user_img = os.path.join(Cfg.main_app.users_fs_path, f'USER_FOLDER_{user_id}', user.user_img)

    return FileResponse(path_to_user_img)

  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth token')
