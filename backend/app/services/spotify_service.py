from urllib import response
from ..config import Config
from typing import List, Dict, Any
import base64
import requests


class SpotifyService:
    def __init__(self):
        self.client_id = Config.SPOTIFY_CLIENT_ID
        self.client_secret = Config.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = Config.SPOTIFY_REDIRECT_URI
        self.spotify_api_base = "https://api.spotify.com/v1"

    def get_spotify_auth_url(self):
        """
        Método que genera la URL de autorización de Spotify para el flujo OAuth.

        Esta URL debe ser utilizada por el frontend para redirigir al usuario a Spotify para que otorgue permisos a la aplicación.
        """
        scope = "user-read-recently-played user-top-read"
        auth_url = (
            "https://accounts.spotify.com/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scope}"
            f"&show_dialog=true"
        )
        return auth_url

    def get_token_from_code(self, code: str) -> Dict[str, Any]:
        """
        Método que intercambia el código de autorización por un token de acceso.

        Realiza una solicitud POST al endpoint de Spotify para obtener el token de acceso utilizando el código recibido tras la autorización del usuario. Este token permitirá realizar solicitudes autenticadas a la API de Spotify en nombre del usuario.
        """
        token_url = "https://accounts.spotify.com/api/token"
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Método que se encarga de obtener un nuevo access token sin requerir que el usuario vuelva a autenticarse manteniendo la sesión activa.
        """
        token_url = "https://accounts.spotify.com/api/token"
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def _auth_headers(self, access_token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    def get_recently_played(
        self, access_token: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Método que obtiene las canciones reproducidas recientemente por el usuario.
        """
        url = f"{self.spotify_api_base}/me/player/recently-played"
        params = {"limit": limit}
        response = requests.get(
            url, headers=self._auth_headers(access_token), params=params
        )
        response.raise_for_status()
        data = response.json().get("items", [])
        tracks = []
        for item in data:
            track = item["track"]
            tracks.append(
                {
                    "id": track["id"],
                    "name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "album": track["album"]["name"],
                    "duration_ms": track["duration_ms"],
                    "played_at": item.get("played_at"),
                }
            )
        return tracks

    def get_audio_features_for_track_ids(
        self, access_token: str, track_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Método que obtiene las características de audio para una de las canciones dadas sus Ids.
        """
        if not track_ids:
            return {}

        unique_track_ids = list(set(track_ids))
        chunk_size = 100  # Spotify solo permite hasta 100 IDs por request
        result = {}
        for i in range(0, len(unique_track_ids), chunk_size):
            chunk = unique_track_ids[
                i : i + chunk_size
            ]  # lista con ids de 0 a 100, luego de 100 a 200, etc
            ids_param = ",".join(chunk)
            url = f"{self.spotify_api_base}/audio-features"
            try:
                response = requests.get(
                    url,
                    headers=self._auth_headers(access_token),
                    params={"ids": ids_param},
                )
                response.raise_for_status()

            except requests.exceptions.HTTPError as e:
                print("Error al obtener audio features:", e)
                print("Respuesta:", response.text)
                raise
            items = response.json().get("audio_features", [])
            for feat in items:
                if feat is None:
                    continue
                track_id = feat.get("id")
                result[track_id] = {
                    "danceability": feat.get("danceability"),
                    "energy": feat.get("energy"),
                    "key": feat.get("key"),
                    "loudness": feat.get("loudness"),
                    "mode": feat.get("mode"),
                    "speechiness": feat.get("speechiness"),
                    "acousticness": feat.get("acousticness"),
                    "instrumentalness": feat.get("instrumentalness"),
                    "liveness": feat.get("liveness"),
                    "valence": feat.get("valence"),
                    "tempo": feat.get("tempo"),
                    "duration_ms": feat.get("duration_ms"),
                }
        return result

    def get_tracks_with_features(
        self, access_token: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Método que obtiene las canciones reproducidas recientemente junto con sus características de audio.
        """
        tracks = self.get_recently_played(
            access_token, limit=limit
        )  # Obtenemos las canciones
        ids = [
            t["id"] for t in tracks if t.get("id")
        ]  # Extramos los Ids de las canciones
        print(ids)
        features_map = self.get_audio_features_for_track_ids(
            access_token, ids
        )  # Obtenemos las características de las canciones
        for t in tracks:  # Asociamos las características a cada canción
            t["audio_features"] = features_map.get(t["id"], {})
        return tracks
