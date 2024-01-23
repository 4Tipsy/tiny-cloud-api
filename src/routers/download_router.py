

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal



# modules
from src.dependencies.auth import auth
from src.dependencies.validate_fs_entity_path import validate_fs_entity_path
from src.models.FsEntityModel import FileModel
from src.controllers.FileController import FileController
from src.controllers.DbController import DbController






router = APIRouter(prefix="/api/download-service", tags=["Download service"])




class _BaseRes(BaseModel):
  result: Literal["success"]















class _DownloadFileReq(BaseModel):
  """_request"""
  fs_entity: FileModel
  file_field: Literal["mere", "special", "temporary"]

# ROUTER FUNCTION
@router.post("/download-file", description="**(Auth needed)**")
def handle_download_file(request: _DownloadFileReq,
                         fs_entity_validated_rel_path=Depends(validate_fs_entity_path),
                         user_id=Depends(auth)
                        ) -> StreamingResponse:
  


  file_stream_iter = FileController.stream_download_file(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)


  # return 200
  return StreamingResponse(file_stream_iter)