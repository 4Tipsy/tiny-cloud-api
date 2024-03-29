

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal



# modules
from src.dependencies.auth import auth
from src.dependencies.validate_fs_entity_path import validate_fs_entity_path
from src.models.FsEntityModel import FileModel, FolderModel, FsEntityModel
from src.controllers.FileController import FileController
from src.controllers.FolderController import FolderController
from src.controllers.DbController import DbController, DbNotFoundException






router = APIRouter(prefix="/api/download-service", tags=["Download service"])




class _BaseRes(BaseModel):
  result: Literal["success"]















class _DownloadFileReq(BaseModel):
  """_request"""
  fs_entity: FileModel
  file_field: Literal["mere", "special", "temporary"]



# ROUTER FUNCTION
@router.post("/download-file", description="**(Auth needed)**", response_description="Binary file stream")
def handle_download_file(request: _DownloadFileReq,
                         fs_entity_validated_rel_path=Depends(validate_fs_entity_path),
                         user_id=Depends(auth)
                        ) -> bytes:
  


  # get entity from db
  try:
    fs_entity_from_db = DbController.get_fs_entity(user_id, request.file_field, request.fs_entity.abs_path, request.fs_entity.base_type)
  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} does not exist")
  
  fs_entity_from_db = FsEntityModel(**fs_entity_from_db)
  

  # read file as stream
  file_size_in_b, file_stream_gen = FileController.stream_download_file(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)
  



  # return 200
  headers = {
    "Content-Length": str(int(file_size_in_b)), # size in bytes
  }
  return StreamingResponse(content=file_stream_gen, media_type=fs_entity_from_db.mime_type, headers=headers)











class _DownloadFolderReq(BaseModel):
  """_request"""
  fs_entity: FolderModel
  file_field: Literal["mere", "special", "temporary"]



# ROUTER FUNCTION
@router.post("/download-folder", description="**(Auth needed)**", response_description="Binary file stream")
def handle_download_file(request: _DownloadFolderReq,
                         fs_entity_validated_rel_path=Depends(validate_fs_entity_path),
                         user_id=Depends(auth)
                        ) -> bytes:
  


  # get entity from db
  try:
    fs_entity_from_db = DbController.get_fs_entity(user_id, request.file_field, request.fs_entity.abs_path, request.fs_entity.base_type)
  except DbNotFoundException as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {request.fs_entity.base_type} does not exist")
  
  fs_entity_from_db = FsEntityModel(**fs_entity_from_db)
  

  # read file as stream
  (file_size_in_b, file_stream_gen) = FolderController.stream_download_folder(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)
  



  # return 200
  headers = {
    "Content-Length": str(int(file_size_in_b)), # size in bytes
  }
  return StreamingResponse(content=file_stream_gen, media_type="application/zip", headers=headers)