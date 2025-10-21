from fastapi import APIRouter
from app.services import SpotifyService

router = APIRouter()
spotify_service = SpotifyService()


@router.get("/")
async def get_spotify_auth_url():
    """
    Endpoint para obtener la URL de autorización de Spotify.
    """
    return spotify_service.get_spotify_auth_url()


@router.get("/callback")
async def get_spotify_code(code: str):
    """
    Endpoint que recibe 'code' que envía Spotify tras la autorización del usuario.
    """

    token_data = spotify_service.get_token_from_code(code)
    return token_data

@router.get("/refresh_token")
async def refresh_access_token(refresh_token: str):
    """
    Endpoint para refrescar el token de acceso utilizando el refresh token.
    """
    new_token_data = spotify_service.refresh_access_token(refresh_token)
    return new_token_data

@router.get("/test")
async def test_endpoint(access_token: str, limit: int = 20):
    """
    Endpoint de prueba para verificar que el servicio de Spotify funciona correctamente.
    """
    return spotify_service.get_tracks_with_features(access_token, limit=limit)