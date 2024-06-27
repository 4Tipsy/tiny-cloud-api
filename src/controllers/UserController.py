
from fastapi import HTTPException, status
import jwt
import os, shutil

# modules
from src.cfg import Cfg
from src.controllers.DbController import DbController, DbNotFoundException
from src.models.UserModel import UserModel
from src.utils.HashingPassword import HashingPassword






class UserController:
  


  @staticmethod
  def _create_new_user_fs(user_id):

    path_to_new_user_folder = os.path.join( Cfg.main_app.users_fs_path, f"USER_FOLDER_{user_id}")
    os.mkdir(path_to_new_user_folder)

    os.mkdir( os.path.join(path_to_new_user_folder, "__mere__") )
    DbController.register_new_structure(user_id, "mere", '/')

    os.mkdir( os.path.join(path_to_new_user_folder, "__special__") )
    DbController.register_new_structure(user_id, "special", '/')

    os.mkdir( os.path.join(path_to_new_user_folder, "__temporary__") )
    DbController.register_new_structure(user_id, "temporary", '/')

    # copy default user img
    shutil.copyfile(
      os.path.join("_data/files", Cfg.new_user.default_user_img_name),
      os.path.join(path_to_new_user_folder, Cfg.new_user.default_user_img_name) 
    )






  @staticmethod
  def create_new_user(user_email, password, user_name) -> None | HTTPException:
    
    hashed_password = HashingPassword.get_hashed_password(password)

    new_user_id = DbController.create_new_user(user_email, hashed_password, user_name)
    UserController._create_new_user_fs(new_user_id)





  @staticmethod
  def get_a_token(user_email, password) -> str | HTTPException:

    # get user from db
    try:
      user = DbController.get_user_by_mail(user_email)
    # if not found the user
    except DbNotFoundException as e:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password or email is wrong")


    # check if password is valid
    hashed_password_from_db = user.hashed_password
    is_password_valid = HashingPassword.check_if_password_valid(password, hashed_password_from_db)
    # if not valid
    if not is_password_valid:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password or email is wrong") 


    # create jwt
    payload = {
      "user_id": user.user_id,
      "jwt_epoch": user.jwt_epoch
    }
    a_token = jwt.encode(payload, Cfg.main_app.jwt_secret, algorithm="HS256")


    return a_token
