
import re


def validate_email(email: str) -> bool:


  # if failed
  if not re.match("[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email):
    return False
  


  return True