from pydantic import BaseModel




class _MainApp(BaseModel):
  port: int
  users_fs_path: str
  hashed_links_len: int
  max_folder_size_to_be_downloadable: int

  jwt_secret: str
  password_hash_secret: str


class _Database(BaseModel):
  port: int
  host: str
  db_name: str
  password: str


class _NewUser(BaseModel):
  default_space_available: float
  default_user_img_name: str









class CfgModel(BaseModel):
  main_app: _MainApp
  database: _Database
  new_user: _NewUser