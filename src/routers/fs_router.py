
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status, Header
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from typing import Literal, Union



# modules
from src.dependencies.auth import auth
from src.dependencies.validate_fs_entity_path import validate_fs_entity_path
from src.controllers.FolderController import FolderController
from src.controllers.FileController import FileController
from src.controllers.DbController import DbController, DbNotFoundException
from src.models.FsEntityModel import FolderModel, FileModel, FsEntityModel, FsEntityInReqModel

from src.dependencies.validate_fs_entity_path import _Req as _ValidateFsEntityPathReq_crutch





router = APIRouter(prefix="/api/fs-service", tags=["File system service"])




class _BaseRes(BaseModel):
  result: Literal["success"]






class _CreateFolderReq(BaseModel):
  """_request"""
  fs_entity: FolderModel
  file_field: Literal["mere", "special", "temporary"]

# ROUTE FUNCTION
@router.post("/create-folder", description="**(Auth needed)**")
def handle_create_folder(request: _CreateFolderReq,
                         fs_entity_validated_rel_path=Depends(validate_fs_entity_path),
                         user_id=Depends(auth)
                        ) -> _BaseRes:

  # fs operation
  FolderController.create_folder(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)
  try:
    # try make record in db
    _fs_entity = FsEntityModel( **request.fs_entity.model_dump() ) # only used in DbController.edit_structure()!!!
    DbController.edit_structure(user_id, request.file_field, _fs_entity, action="add")
    DbController.register_new_structure(user_id, request.file_field, request.fs_entity.abs_path)

  except Exception as e:
    # roll back fs operation on fail!!!
    FolderController.delete_folder(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)
    raise e # reraise

  
  # return 200
  return {"result": "success"}







_upload_file_form_desc = """
Sorry for unavailability of schema here...  
`request` is json string. Kind of schema:  
```
{  
  "fs_entity": same as everywhere (base_type="file" of course)
  "file_field: "mere" | "special" | "temporary" 
}
```
Validation still works
"""

class _UploadFileReq(BaseModel):
  """_request"""
  fs_entity: FileModel
  file_field: Literal["mere", "special", "temporary"]

def _upload_file_form(request: str = Form( description=_upload_file_form_desc )):
  try:
    return _UploadFileReq.model_validate_json(request)
  except ValidationError as e:
    raise HTTPException(
        detail=jsonable_encoder(e.errors()),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


# ROUTER FUNCTION
@router.post("/upload-file", description="**(Auth needed)**")
def handle_upload_file(request: _UploadFileReq=Depends(_upload_file_form),
                       user_id=Depends(auth),
                       file: UploadFile = File( description="Requires `Content-Type` header as FastApi takes mime-type of file from there" ),
                       content_type: Union[str, None] = Header(default=None)
                      ) -> _BaseRes:

  fs_entity_validated_rel_path = validate_fs_entity_path( _ValidateFsEntityPathReq_crutch( **request.model_dump()) ) # CRUTCH!
  
  if not content_type:
    # if no Content-Type header
    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Please provide \"Content-Type\" header.")


  # fill fs_entity (cuz its file)
  fs_entity = FsEntityModel( **request.fs_entity.model_dump() )
  fs_entity.mime_type = file.content_type
  fs_entity.size_in_mb = file.size / 1024 / 1024

  # fs operation
  FileController.upload_file(fs_entity, fs_entity_validated_rel_path, request.file_field, user_id, file=file)
  try:
    # try make record in db
    DbController.edit_structure(user_id, request.file_field, fs_entity, action="add")
    DbController.change_user_used_space(user_id, fs_entity.size_in_mb, action="+")

  except Exception as e:
    # roll back fs operation on fail!!!
    FileController.delete_file(fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)
    raise e # reraise


  # return 200
  return {"result": "success"}








class _RenameEntityReq(BaseModel):
  """_request"""
  fs_entity: FsEntityInReqModel
  file_field: Literal["mere", "special", "temporary"]
  new_name: str

# ROUTER FUNCTION
@router.post("/rename-entity", description="**(Auth needed)**")
def handle_rename_entity(request: _RenameEntityReq,
                         fs_entity_validated_rel_path=Depends(validate_fs_entity_path),
                         user_id=Depends(auth)
                        ) -> _BaseRes:

  # fs operation
  if request.fs_entity.base_type == "folder":
    FolderController.rename_folder(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id, new_name=request.new_name)
  if request.fs_entity.base_type == "file":
    FileController.rename_file(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id, new_name=request.new_name)

  try:
    # try to make record in db
    DbController.edit_structure(user_id, request.file_field, request.fs_entity, action="rename", new_name=request.new_name)

  except Exception as e:
    # roll back fs operation on fail!!!
    old_name = request.fs_entity.name
    request.fs_entity.name = request.new_name # as name was changed in fs

    if request.fs_entity.base_type == "folder":
      FolderController.rename_folder(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id, new_name=old_name)
    if request.fs_entity.base_type == "file":
      FileController.rename_file(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id, new_name=old_name)

    raise e # reraise


  # return 200
  return {"result": "success"}









class _DeleteEntityReq(BaseModel):
  """_request"""
  fs_entity: FsEntityInReqModel
  file_field: Literal["mere", "special", "temporary"]

# ROUTER FUNCTION
@router.post("/delete-entity", description="**(Auth needed)**")
def handle_delete_entity(request: _DeleteEntityReq,
                         fs_entity_validated_rel_path=Depends(validate_fs_entity_path),
                         user_id=Depends(auth)
                        ) -> _BaseRes:
  

  # THIS ONE IS HARD TO HANDLE!!! SO LETS HOPE DB NEVER FALLS
  # fs operation
  if request.fs_entity.base_type == "folder":
    FolderController.delete_folder(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)

  if request.fs_entity.base_type == "file":
    file_size_in_mb = FileController.delete_file(request.fs_entity, fs_entity_validated_rel_path, request.file_field, user_id)

    # i work after fs operation! path exists
    DbController.change_user_used_space(user_id, file_size_in_mb, action="-")




  # i have to work
  DbController.edit_structure(user_id, request.file_field, request.fs_entity, action="del")
  if request.fs_entity.base_type == "folder":
    # if its folder, delete its structure
    DbController.delete_structure(user_id, request.file_field, request.fs_entity.abs_path)



  # return 200
  return {"result": "success"}







