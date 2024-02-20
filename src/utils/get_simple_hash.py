
import string, random




def get_simple_hash(_len: int) -> str:
  """Returns string consisting from [a-z, 0-9] (with length == _len)"""
    
  symbols = string.ascii_lowercase + string.digits # available symbols


  simple_hash = "".join(random.choice(symbols) for _ in range(_len) ) # gen simple hash
  
  return simple_hash