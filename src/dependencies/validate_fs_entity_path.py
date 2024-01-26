

from fastapi import HTTPException, status
from pydantic import BaseModel


# modules
from src.models.FsEntityModel import FsEntityInReqModel
import re, os






class _Req(BaseModel):
  fs_entity: FsEntityInReqModel
  new_name: str | None = None


def validate_fs_entity_path(request: _Req) -> str | HTTPException:
  """
  Checks:
  1) fs_entity.abs_path is abs
  2) [name] == /full/path/to/[name]
  3) name or abs_path consist of [a-zA-z0-9\\\h.,()-_]

  Returns abs_path without all '/' at start of str
  """
    
  # vars
  fs_entity: FsEntityInReqModel = request.fs_entity
  taken_path = fs_entity.abs_path




  # check if path was absolute!
  if taken_path[0] != "/":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Given path should be absolute")
  




  # check if path (or new_name) has inappropriate symbols
  if not re.match("[a-zA-z0-9\\\h.,()-_]", taken_path):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path contains inappropriate symbols")
  if request.new_name:
    if not re.match("[a-zA-z0-9\\\h.,()-_]", request.new_name):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New name contains inappropriate symbols")



  # check if path dirname = name
  if os.path.basename(taken_path) != fs_entity.name:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Given path should contain name of entity in the end")




  
  # validate, aka del '/' from str start (path never should be abs)
  taken_path = taken_path[1:]

  if taken_path[0] == "/":
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Why so many '/' at start of the path, cmon??' (\"{taken_path}\")")


  

  # return
  validated_rel_path = taken_path
  return validated_rel_path
