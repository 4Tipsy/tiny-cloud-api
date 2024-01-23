

import tomllib
from src.models.CfgModel import CfgModel


    

def _load_cfg() -> dict:
  with open("cfg.toml", "rb") as read_file:
    toml = tomllib.load(read_file)
    return toml["cfg"]








# config
Cfg: CfgModel = CfgModel( **_load_cfg() )








# texts
api_docs_main_text = """
  ![img][uwu]

  ### **Tiny-Cloud-API** is just a small FastApi app designed to *store* user files and provide easy way to *share* them around.
  ---
  
  **[!]** Each user has 3 groups to store data in, so called `file_field` (`"mere"`, `"special"`, `"temporary"`).

  **[!]** Errors not related to the validation of the request, although marked with the code `400`, may return other codes (`401`, `403`, `...`), nevertheless, their body remains indelibly typed.

  **[!]** I don't store raw passwords! Only hashed ones, only security. (And i promise not to spam on your email).

  **[!]** Some (many) requests require user authentication. Currently, i use authentication via `JWT`, which are transmitted with cookies. In requests requiring it, this is indicated in the description.

  ---
  My GitHub: [link!][my-github]  
  Source code: [link!][source-code]  
  UwU: [link!][uwu]  

  ---
  [Swagger doc][doc-url]  
  [Redoc][redoc-url]  
  ---
  API routes are below. You can make requests from wherever, whether it is `curl`, our [**cli app (not made yet...)**][get-cli] or something else! Have fun <3


  [my-github]: https://github.com/4Tipsy
  [source-code]: https://github.com/4Tipsy/tiny-cloud-api

  [uwu]: /api/utils-service/uwu

  [get-cli]: #

  [doc-url]: /api/docs
  [redoc-url]: /api/redoc
  """