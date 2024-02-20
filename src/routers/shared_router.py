
from fastapi import APIRouter, Depends, File, UploadFile, Response, HTTPException, status
from pydantic import BaseModel
from typing import Literal


# modules
from src.dependencies.auth import auth
from src.dependencies.validate_fs_entity_path import validate_fs_entity_path
from src.controllers.DbController import DbController, DbNotFoundException, SharedParamAlreadySetException
from src.models.FsEntityModel import FsEntityInReqModel
from src.models.UserModel import SharedDictModel





router = APIRouter(prefix="/api/shared-service", tags=["Shared service"])

class _BaseRes(BaseModel):
  result: Literal["success"]






class _MakeSharedReq(BaseModel):
  fs_entity: FsEntityInReqModel
  file_field: Literal["mere", "special", "temporary"]

class _MakeSharedRes(BaseModel):
  result: Literal["success"]
  hashed_link: str

# router function
@router.post("/make-shared", description="**(Auth needed)**")
def handle_make_shared(request: _MakeSharedReq,
                      user_id=Depends(auth)
                      ) -> _MakeSharedRes:

  try:
    DbController.change_fs_entity_shared_param(user_id, request.file_field, request.fs_entity.abs_path, request.fs_entity.base_type, "share")
    hashed_link = DbController.register_new_shared(user_id, request.fs_entity.base_type, request.fs_entity.abs_path, request.file_field)


  except SharedParamAlreadySetException:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} is already shared")
  except DbNotFoundException:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} not exist")
  

  # if ok
  return {"result": "success", "hashed_link": hashed_link}
  




class _MakeUnsharedReq(BaseModel):
  fs_entity: FsEntityInReqModel
  file_field: Literal["mere", "special", "temporary"]

# router function
@router.post("/make-unshared", description="**(Auth needed)**")
def handle_make_shared(request: _MakeUnsharedReq,
                      user_id=Depends(auth)
                      ) -> _BaseRes:

  try:
    DbController.change_fs_entity_shared_param(user_id, request.file_field, request.fs_entity.abs_path, request.fs_entity.base_type, "unshare")
    shared_dict = DbController.entity_data_to_shared_dict(user_id, request.fs_entity.base_type, request.fs_entity.abs_path, request.file_field)
    DbController.delete_shared_dict(user_id, shared_dict.hashed_link)


  except SharedParamAlreadySetException:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} is already NOT shared")
  except DbNotFoundException:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} not exist")
  

  # if ok
  return {"result": "success"}





class _RemindHashedLinkReq(BaseModel):
  fs_entity: FsEntityInReqModel
  file_field: Literal["mere", "special", "temporary"]

class _RemindHashedLinkRes(BaseModel):
  result: Literal["success"]
  hashed_link: str

# router function
@router.post("/remind-hashed-link", description="**(Auth needed)**")
def handle_make_shared(request: _RemindHashedLinkReq,
                      user_id=Depends(auth)
                      ) -> _RemindHashedLinkRes:
  
  try:

    shared_dict = DbController.entity_data_to_shared_dict(user_id, request.fs_entity.base_type, request.fs_entity.abs_path, request.file_field)
    return {"result": "success", "hashed_link": shared_dict.hashed_link}


  except DbNotFoundException:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} not exist")