# Tiny Cloud API
[this-cool-pink-color]: #FF005C

<img src="http://tiny-cloud.xyz/api/utils-service/uwu" alt="uwu.png">

---
It's is a small REST API designed to *store* user files and provide easy way to *share* them around.  
Made with FastAPI and MongoDB under the hood (huge python project of mine yay).

You can check `api/docs` (routes) here:  
- Swagger: [http://tiny-cloud.xyz/api/docs](http://tiny-cloud.xyz/api/docs)  
- Redoc: [http://tiny-cloud.xyz/api/redoc](http://tiny-cloud.xyz/api/redoc)

API is opened to interact from where ever, so you can easily work with it from `curl` or my [**CLI**][cli-repo-url] *(another my project)*.

**Web client also available!** `check it <3` [http://tiny-cloud.xyz/client](http://tiny-cloud.xyz/client)

[cli-repo-url]: https://github.com/4Tipsy/tiny-cloud-cli

---
## Quick user manual

API has many end-points divided into several services (for convenience).  
To-get and to-return data models can be found in `api/docs` above.

User files could be **shared** via special route (user should assign them sharable first).  
Getting info by: `http://tiny-cloud.xyz/shared/{user_name}/{hashed_link}`  (free to watch for everyone with the link, no authentication needed).  
Downloading by: `http://tiny-cloud.xyz/shared/{user_name}/{hashed_link}/file` (free to download for everyone with the link, no authentication needed).  

---

You may download *and share* folders only up to `Cfg.main_app.max_folder_size_to_be_downloadable`(in MB) size. It was made to avoid extra RAM usage, as downloading a folder requires it's pre-archiving...

---

Each user file storage divided into 3 `file_field`'s - *mere*, *special* and *temporary*:
* `mere` is for file-wasteland and any other mere stuff
* `special` is for important data you wanna store for long *(like, what you use google drive for?)*
* `temporary` name talks for itself, it's for temporary files *(ones you sharing with someone, for example)*

(you still free to use them as you wish)

**All `file_field`'s share same `user.space_available` amount, so perceive them as some *super-folders* in your cloud file system.**

---
Users (and their file system info) stored in MongoDB. User authentication is made with JWT, transferred with cookies.

**Passwords are stored in hashed way**, and each user has `jwt_epoch` field (int). It can be raised `+1`, what will automatically make all JWT's related to this user invalid (if someone will steal JWT, for example).

---

## Some tech-docs

If you want some brief tech documentation, here goes the [link](#)!  
(Feel free to check the code by yourself, it's well-commented <3)