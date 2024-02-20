
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, create_model


# modules
from src.controllers.DbController import DbController, DbNotFoundException
from src.controllers.FileController import FileController
from src.controllers.FolderController import FolderController
from src.models.FsEntityModel import FsEntityModel
from src.models.UserModel import SharedDictModel
from src.dependencies.validate_fs_entity_path import validate_fs_entity_path





router = APIRouter(tags=["Shared service"])




@router.get("/share/{user_name}/{hashed_link}")
def handle_share(user_name: str, hashed_link: str) -> FsEntityModel:
  
  try:
    user = DbController.get_user_by_name(user_name)
    shared_dict = DbController.hashed_link_to_shared_dict(user.user_id, hashed_link)
    fs_entity = FsEntityModel( **DbController.get_fs_entity(user.user_id, shared_dict.file_field, shared_dict.abs_path_to_entity, shared_dict.base_type) )


    if not fs_entity.shared:
      DbController.delete_shared_dict(user.user_id, hashed_link)
      raise HTTPException(404)


    # if ok
    return fs_entity.model_dump(exclude_none=True)



  except DbNotFoundException:
    raise HTTPException(404)
  






@router.get("/share/{user_name}/{hashed_link}/file")
def handle_share_download_file(user_name: str, hashed_link: str) -> bytes:
    
  try:
    user = DbController.get_user_by_name(user_name)
    shared_dict = DbController.hashed_link_to_shared_dict(user.user_id, hashed_link)
    fs_entity = FsEntityModel( **DbController.get_fs_entity(user.user_id, shared_dict.file_field, shared_dict.abs_path_to_entity, shared_dict.base_type) )


    if not fs_entity.shared:
      DbController.delete_shared_dict(user.user_id, hashed_link)
      raise HTTPException(404)


    # if ok
    _Model = create_model("_", fs_entity=(FsEntityModel, ...), new_name=(str, None)) # crutch!!!
    fs_entity_validated_rel_path = validate_fs_entity_path( _Model(fs_entity=fs_entity) ) # crutch!!!

    # # get file generator
    if fs_entity.base_type == "file":
      file_size_in_b, file_stream_gen = FileController.stream_download_file(fs_entity, fs_entity_validated_rel_path, shared_dict.file_field, user.user_id)
      _mime_type = fs_entity.mime_type
    else:
      file_size_in_b, file_stream_gen = FolderController.stream_download_folder(fs_entity, fs_entity_validated_rel_path, shared_dict.file_field, user.user_id)
      _mime_type = "application/zip"

    # # return
    headers = {
      "Content-Length": str(int(file_size_in_b)), # size in bytes
    }
    return StreamingResponse(content=file_stream_gen, media_type=_mime_type, headers=headers)



  # if no such shared file
  except DbNotFoundException:
    raise HTTPException(404)