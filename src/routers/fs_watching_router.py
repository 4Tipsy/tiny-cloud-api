
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Literal, List
import re



# modules
from src.dependencies.auth import auth
from src.models.FsEntityModel import FsEntityModel
from src.controllers.DbController import DbController, DbNotFoundException







router = APIRouter(prefix="/api/fs-watching-service", tags=["File system watching service"])












class _GetFsLayerReq(BaseModel):
  """_request"""
  abs_path_to_layer: str
  file_field: Literal["mere", "special", "temporary"]

class _GetFsLayerRes(BaseModel):
  """_response"""
  result: Literal["success"]
  fs_layer: List[FsEntityModel]

# ROUTER FUNCTION
@router.post("/get-fs-layer", description="**(Auth needed)**")
def handle_get_fs_layer(request: _GetFsLayerReq,
                         user_id=Depends(auth)
                       ) -> _GetFsLayerRes:


  # if invalid path
  if not re.match("[a-zA-z0-9\\\h.,()-_]", request.abs_path_to_layer):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path contains inappropriate symbols")


  # try get fs layer from db
  try:
    fs_layer_structure = DbController.get_fs_layer(user_id, request.file_field, request.abs_path_to_layer)

  # if failed
  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Such path does not exists")


  # return 200
  return {"result": "success", "fs_layer": fs_layer_structure}










class _GetFsEntityReq(BaseModel):
  """_request"""
  abs_path_to_fs_entity: str
  fs_entity_base_type: Literal["file", "folder"]
  file_field: Literal["mere", "special", "temporary"]

class _GetFsEntityRes(BaseModel):
  """_response"""
  result: Literal["success"]
  fs_entity: FsEntityModel


# ROUTER FUNCTION
@router.post("/get-fs-entity", description="**(Auth needed)**")
def handle_get_fs_entity(request: _GetFsEntityReq, 
                         user_id=Depends(auth)
                        ) -> _GetFsEntityRes:
  

  # if invalid path
  if not re.match("[a-zA-z0-9\\\h.,()-_]", request.abs_path_to_fs_entity):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path contains inappropriate symbols")


  # try get fs entity from db
  try:
    fs_entity_to_return = DbController.get_fs_entity(user_id, request.file_field, request.abs_path_to_fs_entity, request.fs_entity_base_type)

  # if failed
  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Such path does not exists")
  

  # return 200
  return {"result": "success", "fs_entity": fs_entity_to_return}
