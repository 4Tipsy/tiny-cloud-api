
from tempfile import _TemporaryFileWrapper
import tempfile, zipfile, os


# modules
from src.cfg import Cfg



class FolderToTempArchive:
    

  class _FolderTooLargeException(Exception):
    """Raised when folder is larger than limited"""
    pass
    

  @staticmethod
  def archive(dir_path: str) -> _TemporaryFileWrapper:
    """Archives <dir_path> into temporary file, then returns it.
    Will raise _FolderTooLargeException if folder is bigger than Cfg.main_app.max_folder_size_to_be_downloadable
    """

    temp_file = tempfile.NamedTemporaryFile(dir="_data/temp", suffix=".zip")

    zip_file = zipfile.ZipFile(temp_file.name, "w", zipfile.ZIP_DEFLATED)

    # iterate for folder contents
    total_size = 0
    for (root, dirs, files) in os.walk(dir_path):
      for file in files:
        file_path = os.path.join(root, file)
        print(file_path)

        zip_file.write(file_path, os.path.relpath(file_path, dir_path) ) # add to archive

        total_size += os.path.getsize(file_path) / 1024 / 1024 # add new size
        if total_size > Cfg.main_app.max_folder_size_to_be_downloadable:
          # if folder is too large
          raise FolderToTempArchive._FolderTooLargeException
        
    zip_file.close()

    return temp_file