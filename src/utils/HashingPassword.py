
import bcrypt




class HashingPassword:



  @staticmethod
  def get_hashed_password(password: str) -> str:
    """Return hash made from given password"""  
    
    hash_in_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hash_in_bytes.decode()




  @staticmethod
  def check_if_password_valid(password: str, hashed_password_from_db: str) -> bool:
    """Take password and 'hashed password' from DB, return true if valid"""

    return bcrypt.checkpw(password.encode(), hashed_password_from_db.encode())