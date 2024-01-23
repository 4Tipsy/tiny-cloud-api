

from fastapi import HTTPException, status





class FsLayerController:
    


  @staticmethod
  def _validate_taken_path(raw_path) -> str | HTTPException:
    """Validates raw_path, raise HTTPException if raw_path is not abs. Remove all '/' from start of raw_path to avoid out-of-app fs actions"""
    
    # check if path was absolute!
    if raw_path[0] != "/":
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Given path should be absolute")
    
    # validate, aka del all '/' from str start (path never should be abs)
    while len(raw_path) != 0:

      if raw_path[0] == "/":
        raw_path = raw_path[1:]
      
      else:
        break
    
    return raw_path





  @staticmethod
  def get_fs_layer(abs_path_to_layer, file_field, user_id):

    validated_path = FsLayerController._validate_taken_path(abs_path_to_layer)