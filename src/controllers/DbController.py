
from fastapi import HTTPException, status
from pymongo import MongoClient
from typing import Literal, Optional
import os


# modules
from src.cfg import Cfg
from src.models.UserModel import UserModel
from src.models.FsEntityModel import FsEntityModel







class DbNotFoundException(Exception):
  pass

class AllAvailableSpaceUsedException(Exception):
  pass







class _DbController:
    

  def __init__(self):
    # create connection pool
    client = MongoClient(host=Cfg.database.host, port=Cfg.database.port)
    self.db = client[Cfg.database.db_name]




  














  #
  # GETTING USERS
  #

  def get_user_by_id(self, user_id: int) -> UserModel | DbNotFoundException:
    """Will return user from db"""

    user = self.db["users"].find_one({"user_id": user_id})
    if not user:
      raise DbNotFoundException()

    return UserModel( **user )



  def get_user_by_mail(self, user_email: str) -> UserModel | DbNotFoundException:
    """Will return user from db"""

    user = self.db["users"].find_one({"user_email": user_email})
    if not user:
      raise DbNotFoundException()


    return UserModel( **user )
  
























  #
  # CHANGING USER'S USED_SPACE
  #

  def change_user_used_space(self, user_id, file_size_in_mb, action: Literal["+", "-"]):

    # get user
    user = self.get_user_by_id(user_id)

    if action == "+":
      user.used_space + file_size_in_mb

      if user.used_space > user.available_space:
        # abort operation
        raise AllAvailableSpaceUsedException()


    if action == "-":
      user.used_space - file_size_in_mb


    # make record
    self.db["users"].find_one_and_replace({"user_id": user_id}, user.model_dump())











  #
  # GETTING FS LAYER (or single entity)
  #

  def get_fs_layer(self, user_id, file_field, abs_path_to_layer) -> list | DbNotFoundException:
    """Get structure of given layer"""

    # get structure
    where_key = f"{user_id}::{file_field}::{abs_path_to_layer}"
    structure_keyed = self.db["users-folders-structures"].find_one({"where_key": where_key})

    if not structure_keyed:
      raise DbNotFoundException

    return structure_keyed["structure"]
  



  def get_fs_entity(self, user_id, file_field, abs_path_to_fs_entity, fs_entity_base_type) -> list | DbNotFoundException:
    """Get structure of given layer"""

    # get structure
    abs_path_to_layer = os.path.dirname(abs_path_to_fs_entity)
    where_key = f"{user_id}::{file_field}::{abs_path_to_layer}"
    structure_keyed = self.db["users-folders-structures"].find_one({"where_key": where_key})

    if not structure_keyed:
      raise DbNotFoundException
    

    # find needed entity
    for ent in structure_keyed["structure"]:
      if ent["abs_path"] == abs_path_to_fs_entity:
        if ent["base_type"] == fs_entity_base_type:
          entity_to_return = ent

    if not entity_to_return:
      raise DbNotFoundException


    return entity_to_return




















  #
  # REGISTERING NEW, DELETING, EDITING FS STRUCTURES
  #

  def register_new_structure(self, user_id, file_field, abs_path_to_new_folder) -> None:

    where_key = f"{user_id}::{file_field}::{abs_path_to_new_folder}"
    new_structure_keyed = {"where_key": where_key, "structure": []}
    self.db["users-folders-structures"].insert_one(new_structure_keyed)




  def delete_structure(self, user_id, file_field, abs_path_to_layer) -> None:

    where_key = f"{user_id}::{file_field}::{abs_path_to_layer}"
    self.db["users-folders-structures"].find_one_and_delete({"where_key": where_key})




  def edit_structure(self, user_id, file_field, fs_entity: FsEntityModel, action: Literal["add", "del", "rename"], new_name: Optional[str]=None) -> None:
    """Edit structure info in db, required by any fs operation"""


    # vars
    abs_path_to_layer = os.path.dirname( fs_entity.abs_path )
    where_key = f"{user_id}::{file_field}::{abs_path_to_layer}"


    # get structure
    structure_keyed = self.db["users-folders-structures"].find_one({"where_key": where_key})
    structure = structure_keyed["structure"]


    # modify structure
    if action == "add":
      structure.append(fs_entity.model_dump(exclude_none=True))

    elif action == "del":
      structure = list(filter( 
        lambda ent: not ((ent["name"] == fs_entity.name) and (ent["base_type"] == fs_entity.base_type)),
        structure 
      ))

    elif action == "rename":
      for ent in structure:
        if ent['name'] == fs_entity.name:
          ent['name'] = new_name
    

    # update where_key if needed (if folder renamed)
    # cuz when we rename folder, according structure.where_key should be updated as well
    if action == "rename" and fs_entity.base_type == "folder":

      renamed_folder_where_key = f"{user_id}::{file_field}::{os.path.join(abs_path_to_layer, fs_entity.name)}"

      _structure_keyed = self.db["users-folders-structures"].find_one_and_delete({"where_key": renamed_folder_where_key})
      _structure_keyed["where_key"] = f"{user_id}::{file_field}::{os.path.join(abs_path_to_layer, new_name)}"
      self.db["users-folders-structures"].insert_one(_structure_keyed)
      


    # update structure
    new_structure_keyed = {"where_key": where_key, "structure": structure}
    self.db["users-folders-structures"].find_one_and_replace({"where_key": where_key}, new_structure_keyed)





















  #
  # CREATING USER
  #


  def create_new_user(self, user_email, hashed_password, user_name) -> int | HTTPException:


    # if name or mail is used
    if self.db["users"].find_one({"user_name": user_name}):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Such name is already used")
    
    if self.db["users"].find_one({"user_email": user_email}):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Such mail is already in use")



    # get new user id
    user_id = 0
    while True:
      user_id += 1

      if self.db["users"].find_one({"user_id": user_id}) == None:
        break


    # fill new user obj
    new_user = {
      "verified": False,
      "jwt_epoch": 1,

      "user_id": user_id,
      "user_name": user_name,
      "user_img": Cfg.new_user.default_user_img_name,

      "user_email": user_email,
      "hashed_password": hashed_password,

      "used_space": 0,
      "available_space": Cfg.new_user.default_space_available
    }

    # write in db
    self.db["users"].insert_one(new_user)

    # return the id
    return user_id





DbController = _DbController()
