
import toml
from src.models.CfgModel import CfgModel


    

def _load_cfg() -> dict:
  with open("Config.toml", "r") as read_file:
    config_toml = toml.load(read_file)
    return config_toml["cfg"]



# CONFIG
Cfg: CfgModel = CfgModel( **_load_cfg() )








# text at the start of docs page
api_docs_main_text = f"""
  <img src="/api/utils-service/uwu" alt="uwu.png" style="background-color: #d0d0d0;">

  ### **Tiny-Cloud-API** is just a small FastApi app designed to *store* user files and provide easy way to *share* them around.
  ---
  
  **(!)** Each user has 3 groups to store data in, so called `file_field` (`"mere"`, `"special"`, `"temporary"`).

  **(!)** Errors not related to the validation of the request, although marked with the code `400`, may return other codes (`401`, `403`, `...`), nevertheless, their body remains indelibly typed.

  **(!)** I don't store raw passwords! Only hashed ones. (And i promise not to spam on your email).

  **(!)** Some (many) requests require user authentication. Currently, i use authentication via `JWT`, which are transmitted with cookies (`a-token` cookie). In requests requiring it, this is indicated in the description.

  **(!)** You may download *and share* folders only up to `{Cfg.main_app.max_folder_size_to_be_downloadable} MB` size. It was made to avoid extra RAM usage, as downloading a folder requires it's pre-archiving...

  ---
  My GitHub: [link!][my-github]  
  App's repo: [link!][source-code]  
  UwU: [link!](/api/utils-service/uwu)  

  ---
  [Swagger doc][doc-url]  
  [Redoc][redoc-url]  
  ---
  API routes are below. You can make requests from wherever, whether it is `curl`, our [**cli app**][get-cli] or something else! Have fun <3


  [my-github]: https://github.com/4Tipsy
  [source-code]: https://github.com/4Tipsy/tiny-cloud-api

  [get-cli]: https://github.com/4Tipsy/tiny-cloud-cli

  [doc-url]: /api/docs
  [redoc-url]: /api/redoc
  """
