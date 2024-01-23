
from pydantic import BaseModel
from typing import Literal, Optional




class FsEntityModel(BaseModel):
    
  name: str
  abs_path: str

  base_type: Literal["folder", "file"]

  size_in_mb: Optional[float] = None
  mime_type: Optional[str] = None



class FsEntityInReqModel(BaseModel):
    
  name: str
  abs_path: str

  base_type: Literal["folder", "file"]




class FileModel(BaseModel):
  name: str
  abs_path: str

  base_type: Literal["file"]


class FolderModel(BaseModel):
  name: str
  abs_path: str

  base_type: Literal["folder"]









