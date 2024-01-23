
from fastapi import HTTPException, status, UploadFile
import os, shutil


# modules
from src.models.FsEntityModel import FileModel
from src.cfg import Cfg






class FileController():






  @staticmethod
  def _construct_full_path(validated_rel_path, user_id, file_field) -> str | HTTPException:
    """Will return abs path to chosen fs_layer. Aka path where action should occur"""

    user_folder = f"USER_FOLDER_{user_id}"
    file_field = f"__{file_field}__"
    return os.path.join(Cfg.main_app.users_fs_path, user_folder, file_field, validated_rel_path)









  @staticmethod
  def upload_file(fs_entity: FileModel, fs_entity_validated_rel_path, file_field, user_id, file: UploadFile) -> None | HTTPException:

    # construct full path
    full_path = FileController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if already exists
    if os.path.isfile(full_path) == True:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} already exists")

    # create folder
    with open(full_path, "wb") as new_file:
      while chunk := file.file.read(1024 * 1024):
        new_file.write(chunk)







  @staticmethod
  def rename_file(fs_entity: FileModel, fs_entity_validated_rel_path, file_field, user_id, new_name) -> None | HTTPException:
    
    # construct full path
    full_path = FileController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if not exist
    if os.path.isfile(full_path) == False:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} does not exist")

    # rename folder
    new_full_path = os.path.join( os.path.dirname(full_path), new_name)
    os.rename(full_path, new_full_path)





  @staticmethod
  def delete_file(fs_entity: FileModel, fs_entity_validated_rel_path, file_field, user_id) -> float | HTTPException:
        
    # construct full path
    full_path = FileController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if not exist
    if os.path.isfile(full_path) == False:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} does not exist")

    # delete file
    file_size_in_mb = os.path.getsize(full_path) / 1024 / 1024
    os.remove(full_path)
    return file_size_in_mb # for db operations
  




  @staticmethod
  def stream_download_file(fs_entity: FileModel, fs_entity_validated_rel_path, file_field, user_id) -> iter:
        
    # construct full path
    full_path = FileController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if not exist
    if os.path.isfile(full_path) == False:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} does not exist")

    # STREAM file
    with open(full_path, "rb") as stream_file:
      yield stream_file.read()