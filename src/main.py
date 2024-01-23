

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from typing import Literal


# modules
from src.cfg import Cfg, api_docs_main_text
from src.routers.fs_router import router as fs_router
from src.routers.fs_watching_router import router as fs_watching_router
from src.routers.download_router import router as download_router
from src.routers.user_router import router as user_router
from src.routers.utils_router import router as utils_router







# default on_error response model | pls, define me before app
class OnErrorResModel(BaseModel):
  result: Literal['error']
  error: str




app = FastAPI(
  docs_url="/api/docs", # check routers/docs.py
  redoc_url="/api/redoc", # check routers/docs.py
  openapi_url="/api/open-api",

  title="Tiny Cloud API",
  version="API 0.1.0",
  description=api_docs_main_text,

  responses={400: {'model': OnErrorResModel}},
)


# cors
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)







app.include_router(fs_router)
app.include_router(fs_watching_router)
app.include_router(download_router)
app.include_router(user_router)
app.include_router(utils_router)









# 404
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException) -> str:
  return JSONResponse(
      status_code=404,
      content={'result': 'error', 'error': '404'}
    )

# error response
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> OnErrorResModel:
  return JSONResponse(
      status_code=exc.status_code,
      content={'result': 'error', 'error': exc.detail}
    )

# server error
@app.exception_handler(Exception)
async def internal_server_exception_handler(request: Request, exc: HTTPException) -> OnErrorResModel:
  return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={'result': 'error', 'error': 'Internal server error'}
    )










if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=Cfg.main_app.port)