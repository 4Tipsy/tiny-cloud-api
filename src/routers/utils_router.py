

from fastapi import APIRouter
from fastapi.responses import FileResponse






router = APIRouter(prefix="/api/utils-service", tags=["Utils service"])







@router.get("/uwu", include_in_schema=False)
def handle_uwu() -> FileResponse:
  return FileResponse("src/utils/_files/uwu.png")


@router.get("/404", include_in_schema=False)
def handle_uwu() -> FileResponse:
  return FileResponse("src/utils/_files/404.png")