from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.services import SpotifyService

spotify_router = APIRouter()
spotify_service = SpotifyService()


@spotify_router.get("/")
async def get_spotify_auth_url():
    """
    Endpoint para obtener la URL de autorización de Spotify.
    """
    return spotify_service.get_spotify_auth_url()


@spotify_router.get("/callback")
async def get_spotify_code(code: str):
    token_data = spotify_service.get_token_from_code(code)
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")
    
    # Redirigir al frontend con todos los datos necesarios
    redirect_url = f"http://localhost:5173/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={expires_in}"
    return RedirectResponse(url=redirect_url)

@spotify_router.get("/refresh_token")
async def refresh_access_token(refresh_token: str):
    """
    Endpoint para refrescar el token de acceso utilizando el refresh token.
    """
    new_token_data = spotify_service.refresh_access_token(refresh_token)
    return new_token_data

@spotify_router.get("/test")
async def test_endpoint(access_token: str, limit: int = 20):
    """
    Endpoint de prueba para verificar que el servicio de Spotify funciona correctamente.
    """
    return spotify_service.get_recently_played(access_token, limit=limit)