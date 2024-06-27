

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import FileResponse
from pydantic import create_model

from typing import Literal
import os

# modules
from src.models.FsEntityModel import FsEntityModel
from src.dependencies.auth import auth
from src.dependencies.validate_fs_entity_path import validate_fs_entity_path
from src.controllers.DbController import DbController, DbNotFoundException
from src.cfg import Cfg



router = APIRouter(prefix="/api/utils-service", tags=["Utils service"])







@router.get("/uwu", include_in_schema=False)
def handle_uwu() -> FileResponse:
  return FileResponse("_data/files/uwu.png")


@router.get("/404", include_in_schema=False)
def handle_404() -> FileResponse:
  return FileResponse("_data/files/404.png")




@router.get("/download-img-via-get-route", description="**(auth needed)**")
def handle_download_img_file(abs_path: str, file_field: Literal["mere", "special", "temporary"], user_id=Depends(auth)) -> FileResponse:
  """Exists cuz of <img src={get-route}> shit"""

  try:
    fs_entity = FsEntityModel( **DbController.get_fs_entity(user_id, file_field, abs_path, 'file') )
  except DbNotFoundException:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no such image")


  _EntityModel = create_model("_", fs_entity=(FsEntityModel, ...), new_name=(str, None)) # crutch!!!
  fs_entity_validated_rel_path = validate_fs_entity_path( _EntityModel(fs_entity=fs_entity) ) # crutch!!!


  path_to_img_file = os.path.join( Cfg.main_app.users_fs_path, f'USER_FOLDER_{user_id}', f'__{file_field}__', fs_entity_validated_rel_path )
  return FileResponse(path_to_img_file)
    
