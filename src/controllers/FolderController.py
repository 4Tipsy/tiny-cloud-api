
from fastapi import HTTPException, status
from typing import Generator, Tuple
from tempfile import _TemporaryFileWrapper
import os, shutil, tempfile


# modules
from src.models.FsEntityModel import FolderModel
from src.cfg import Cfg
from src.utils.FolderToTmpArchive import FolderToTempArchive






class FolderController():
    


  




  @staticmethod
  def _construct_full_path(validated_rel_path, user_id, file_field) -> str | HTTPException:
    """Will return abs path to chosen fs_layer. Aka path where action should occur"""

    user_folder = f"USER_FOLDER_{user_id}"
    file_field = f"__{file_field}__"
    return os.path.join(Cfg.main_app.users_fs_path, user_folder, file_field, validated_rel_path)









  @staticmethod
  def create_folder(fs_entity: FolderModel, fs_entity_validated_rel_path, file_field, user_id) -> None | HTTPException:

    # construct full path
    full_path = FolderController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if already exists
    if os.path.isdir(full_path) == True:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} already exists")

    # create folder
    os.mkdir(full_path)







  @staticmethod
  def rename_folder(fs_entity: FolderModel, fs_entity_validated_rel_path, file_field, user_id, new_name) -> None | HTTPException:

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rn disabled, kill me plz, i hate my life")
    
    # construct full path
    full_path = FolderController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if not exist
    if os.path.isdir(full_path) == False:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} does not exist")

    # rename folder
    new_full_path = os.path.join( os.path.dirname(full_path), new_name)
    os.rename(full_path, new_full_path)





  @staticmethod
  def delete_folder(fs_entity: FolderModel, fs_entity_validated_rel_path, file_field, user_id) -> None | HTTPException:

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rn disabled, kill me plz, i hate my life")
        
    # construct full path
    full_path = FolderController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if not exist
    if os.path.isdir(full_path) == False:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} does not exist")

    # delete folder
    shutil.rmtree(full_path)





  @staticmethod
  def stream_download_folder(fs_entity: FolderModel, fs_entity_validated_rel_path, file_field, user_id) -> Tuple[int, Generator[bytes, None, None]]:
        
    # construct full path
    full_path = FolderController._construct_full_path(fs_entity_validated_rel_path, user_id, file_field)

    # check if not exist
    if os.path.isdir(full_path) == False:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Such {fs_entity.base_type} does not exist")


    # transform folder into temp archive
    try:
      temp_archive = FolderToTempArchive.archive(full_path)
    except FolderToTempArchive._FolderTooLargeException:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The folder you try to download is too large, current size limit is {Cfg.main_app.max_folder_size_to_be_downloadable} MB.")

    # STREAM file
    def file_stream_gen():
      with open(temp_archive.name, "rb") as stream_file:
        yield stream_file.read()
        temp_archive.close() # close this already!


    size_in_b = os.path.getsize(temp_archive.name)
    return (size_in_b, file_stream_gen()) # returned val