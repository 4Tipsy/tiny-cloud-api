
from fastapi import HTTPException, status
from pymongo import MongoClient
from typing import Literal, Optional
import os


# modules
from src.cfg import Cfg
from src.models.UserModel import UserModel, SharedDictModel
from src.models.FsEntityModel import FsEntityModel
from src.utils.get_simple_hash import get_simple_hash






class DbNotFoundException(Exception):
  pass

class AllAvailableSpaceUsedException(Exception):
  pass

class SharedParamAlreadySetException(Exception):
  pass






class _DbController:
    

  def __init__(self):
    # create connection pool
    client = MongoClient(host=Cfg.database.host, port=Cfg.database.port)
    self.db = client[Cfg.database.db_name]




  


  #
  # WORKING WITH USER.SHARED
  #

  def hashed_link_to_shared_dict(self, user_id: int, hashed_link: str) -> SharedDictModel | DbNotFoundException:

    user = self.db["users"].find_one({"user_id": user_id})
    user = UserModel( **user )

    # find shared_dict we need
    shared_dict = next(filter( lambda d: d.hashed_link==hashed_link, user.shared), None)

    if not shared_dict:
      raise DbNotFoundException
    
    return shared_dict



  def entity_data_to_shared_dict(self, user_id: int, base_type: Literal["folder", "file"], abs_path_to_entity: str, file_field) -> SharedDictModel | DbNotFoundException:

    user = self.db["users"].find_one({"user_id": user_id})
    user = UserModel( **user )

    # find shared_dict we need
    shared_dict = next(filter(lambda d: (d.base_type==base_type and d.file_field==file_field and d.abs_path_to_entity==abs_path_to_entity), user.shared), None)

    if not shared_dict:
      raise DbNotFoundException
    
    return shared_dict




  def register_new_shared(self, user_id: int, base_type: Literal["folder", "file"], abs_path_to_entity: str, file_field) -> str:

    user = self.db["users"].find_one({"user_id": user_id})
    user = UserModel( **user )

    new_hashed_link = get_simple_hash(Cfg.main_app.hashed_links_len)

    # get unique hashed_link
    _unique = True
    while True:

      for idx, shared_dict in enumerate( user.shared ):

        if shared_dict.hashed_link == new_hashed_link:
          _unique = False

          if idx <= 5:
            # first 5 times, we try to regenerate the hashed_link
            new_hashed_link = get_simple_hash(Cfg.main_app.hashed_links_len)
          else:
            # after 5 times
            new_hashed_link += "B"
          

      # if never matched
      if _unique:
        break

    # insert
    new_shared_dict = SharedDictModel(hashed_link=new_hashed_link, base_type=base_type, file_field=file_field, abs_path_to_entity=abs_path_to_entity)
    user.shared.append(new_shared_dict.model_dump())
    self.db["users"].find_one_and_replace({"user_id": user_id}, user.model_dump())

    return new_hashed_link # return hashed_link of new entity


  def delete_shared_dict(self, user_id: int, hashed_link: str) -> None | DbNotFoundException:

    user = self.db["users"].find_one({"user_id": user_id})
    user = UserModel( **user )

    new_user_shared = list(filter( lambda d: d.hashed_link != hashed_link , user.shared ))

    # if was no d to delete
    if user.shared == new_user_shared:
      raise DbNotFoundException
    
    # save to db
    user.shared = new_user_shared
    self.db["users"].find_one_and_replace({"user_id": user_id}, user.model_dump())







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
  


  def get_user_by_name(self, user_name: str) -> UserModel | DbNotFoundException:
    """Will return user from db"""

    user = self.db["users"].find_one({"user_name": user_name})
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
      user.used_space += file_size_in_mb

      if user.used_space > user.available_space:
        # abort operation
        raise AllAvailableSpaceUsedException()


    if action == "-":
      user.used_space -= file_size_in_mb


    # make record
    self.db["users"].find_one_and_replace({"user_id": user_id}, user.model_dump())











  #
  # GETTING FS LAYER (or single entity)
  #

  def get_fs_layer(self, user_id, file_field, abs_path_to_layer) -> list | DbNotFoundException:
    """Get structure of given layer"""

    # get structure
    where_key = [user_id, file_field, abs_path_to_layer]
    structure_keyed = self.db["users-folders-structures"].find_one({"where_key": where_key})

    if not structure_keyed:
      raise DbNotFoundException

    return structure_keyed["structure"]
  



  def get_fs_entity(self, user_id, file_field, abs_path_to_fs_entity, fs_entity_base_type) -> list | DbNotFoundException:
    """Get structure of given layer"""

    # get structure
    abs_path_to_layer = os.path.dirname(abs_path_to_fs_entity)
    where_key = [user_id, file_field, abs_path_to_layer]
    structure_keyed = self.db["users-folders-structures"].find_one({"where_key": where_key})

    if not structure_keyed:
      raise DbNotFoundException
    

    # find needed entity
    entity_to_return = None
    for ent in structure_keyed["structure"]:
      if ent["abs_path"] == abs_path_to_fs_entity:
        if ent["base_type"] == fs_entity_base_type:
          entity_to_return = ent

    if not entity_to_return:
      raise DbNotFoundException


    return entity_to_return












  #
  # CHANGING SHARED PARAM OF FS_ENTITY
  #

  def change_fs_entity_shared_param(self, user_id, file_field, abs_path_to_fs_entity, fs_entity_base_type, action: Literal["share", "unshare"]) -> None | SharedParamAlreadySetException | DbNotFoundException:
    """Change fs_entity.shared"""

    # get structure
    abs_path_to_layer = os.path.dirname(abs_path_to_fs_entity)
    where_key = [user_id, file_field, abs_path_to_layer]
    structure_keyed = self.db["users-folders-structures"].find_one({"where_key": where_key})
    structure = structure_keyed["structure"]

    if not structure_keyed:
      raise DbNotFoundException
    

    # find needed entity
    entity_to_change_shared_param = None
    for ent in structure:
      if ent["abs_path"] == abs_path_to_fs_entity:
        if ent["base_type"] == fs_entity_base_type:
          entity_to_change_shared_param = ent

    if not entity_to_change_shared_param:
      raise DbNotFoundException
    

    # change fs_entity.shared
    if action == "share":
      # if already set
      if entity_to_change_shared_param["shared"] == True:
        raise SharedParamAlreadySetException

      # set
      entity_to_change_shared_param["shared"] = True



    elif action == "unshare":
      # if already set
      if entity_to_change_shared_param["shared"] == False:
        raise SharedParamAlreadySetException

      # set
      entity_to_change_shared_param["shared"] = False


    # update structure

    new_structure_keyed = {"where_key": where_key, "structure": structure}
    self.db["users-folders-structures"].find_one_and_replace({"where_key": where_key}, new_structure_keyed)










  #
  # REGISTERING NEW, DELETING, EDITING FS STRUCTURES
  #

  def register_new_structure(self, user_id, file_field, abs_path_to_new_folder) -> None:

    where_key = [user_id, file_field, abs_path_to_new_folder]
    new_structure_keyed = {"where_key": where_key, "structure": []}
    self.db["users-folders-structures"].insert_one(new_structure_keyed)




  def delete_structure(self, user_id, file_field, abs_path_to_layer) -> None:

    where_key = [user_id, file_field, abs_path_to_layer]
    self.db["users-folders-structures"].find_one_and_delete({"where_key": where_key})




  def edit_structure(self, user_id, file_field, fs_entity: FsEntityModel, action: Literal["add", "del", "rename"], new_name: Optional[str]=None) -> None:
    """Edit structure info in db, required by any fs operation"""


    # vars
    abs_path_to_layer = os.path.dirname( fs_entity.abs_path )
    where_key = [user_id, file_field, abs_path_to_layer]


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

      renamed_folder_where_key = [user_id, file_field, abs_path_to_layer]

      _structure_keyed = self.db["users-folders-structures"].find_one_and_delete({"where_key": renamed_folder_where_key})
      _structure_keyed["where_key"] = [user_id, file_field, abs_path_to_layer]
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
    new_user = UserModel(
      verified=False,
      jwt_epoch=1,
      user_id=user_id,
      user_name=user_name,
      user_img=Cfg.new_user.default_user_img_name,
      user_email=user_email,
      hashed_password=hashed_password,
      shared=[],
      used_space=0,
      available_space=Cfg.new_user.default_space_available
    )


    # write in db
    self.db["users"].insert_one(new_user.model_dump())

    # return the id
    return user_id





DbController = _DbController()
