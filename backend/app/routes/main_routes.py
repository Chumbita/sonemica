from fastapi import APIRouter
from app.core import main_flow

main_router = APIRouter()

@main_router.get("/analyzer")
async def sonemica_analyzer(access_token: str):
  """
  Endpoint principal
  """

  return main_flow(access_token)