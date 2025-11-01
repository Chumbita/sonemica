import polars as pl
import re
from ftfy import fix_text
from app.services import SpotifyService

# Columnas esperadas en el dataset de audio features
AUDIO_FEATURES_COLUMNS = [
    "Title",
    "Artist",
    "Energy",
    "Danceability",
    "Loudness",
    "Liveness",
    "Valence",
    "Length",
    "Acousticness",
    "Speechiness",
    "Popularity",
]

# Columnas esperadas en el dataset de letras
LYRICS_COLUMNS = [
    "Title",
    "Artist",
    "Lyrics",
]


class DataFetcher:
    """
    Clase encargada de obtener datos musicales del usuario:
    - Canciones reproducidas recientemente desde Spotify
    - Audio features desde dataset local
    - Letras desde dataset local
    """

    def __init__(self):
        self.spotify_service = SpotifyService()
        self.audio_features_df = pl.read_csv(
            "app/data/audio_features_general.csv",
            schema_overrides={"Length": pl.Utf8},
            columns=AUDIO_FEATURES_COLUMNS,
        )

        self.lyrics_df = pl.read_csv(
            "app/data/lyrics_general.csv", columns=LYRICS_COLUMNS
        )

    @staticmethod
    def normalize_lyrics(lyrics: str) -> str:
        """
        Limpia y corrige la codificación de una letra de canción.

        - Elimina saltos de línea y espacios redundantes.
        - Corrige errores de codificación con ftfy.
        """
        if not lyrics:
            return None

        lyrics = fix_text(lyrics)
        lyrics = lyrics.strip()
        lyrics = lyrics.replace("\n", " ").replace("\r", " ")
        lyrics = re.sub(r"\s+", " ", lyrics)

        return lyrics

    def fetch_recent_tracks(self, access_token: str):
        """
        Obtiene las últimas 50 canciones reproducidas por el usuario en Spotify.
        """

        # Hacemos la llamada al servicio de Spotify
        user_50_recently_played_tracks = self.spotify_service.get_recently_played(
            access_token=access_token, limit=50
        )

        return user_50_recently_played_tracks

    def fetch_audio_features(self, tracks: list[dict]):
        """
        Enlaza las canciones provistas con sus características de audio desde el dataset local.

        Devuelve una lista de diccionarios con los datos combinados.
        """

        # Normalización del resultado de spotify ya para agilizar la búsqueda necesitamos un dataframe con las columnas "Title" y "Artist".
        normalized_tracks = [
            {
                "Title": track.get("name", ""),
                "Artist": track["artists"][0] if track.get("artists") else "",
            }
            for track in tracks
        ]

        # Creamos un dataframe con las canciones normalizadas
        normalized_tracks_df = pl.DataFrame(normalized_tracks)

        # Join del dataframe de las canciones normalizadas y el dataframe de audio features
        matched_df = self.audio_features_df.join(
            normalized_tracks_df, on=["Title", "Artist"], how="inner"
        )

        return matched_df.to_dicts()

    def fetch_lyrics(self, tracks: list):
        """
        Enlaza las canciones provistas con sus letras desde el dataset local.

        Devuelve una lista de diccionarios con las letras normalizadas.
        """

        # Normalización del resultado de spotify ya para agilizar la búsqueda necesitamos un dataframe con las columnas "Title" y "Artist".
        normalized_tracks = [
            {
                "Title": track.get("name", ""),
                "Artist": track["artists"][0] if track.get("artists") else "",
            }
            for track in tracks
        ]

        # Creamos un dataframe con las canciones normalizadas
        normalized_tracks_df = pl.DataFrame(normalized_tracks)

        # Join del dataframe de las canciones normalizadas y el dataframe de las lyrics
        matched_df = self.lyrics_df.join(
            normalized_tracks_df, on=["Title", "Artist"], how="inner"
        )

        lyrics_data = matched_df.to_dicts()

        # Limpiamos las canciones
        for track in lyrics_data:
            track["Lyrics"] = self.normalize_lyrics(track["Lyrics"])

        return lyrics_data


# Prueba unitaria
""" if __name__ == "__main__":
    data_fetcher = DataFetcher()

    tracks = data_fetcher.fetch_recent_tracks(
        "BQCPL9va0jq1pLRjN1j4PYxYkGBz7dyCiQWqMsCwnuPqx25CQwhDK69RYmqObold7zLwUhQQ308DcgLEGEMmFmXXg30jCw2pblrMWfbtnXDUCiCIy9qwB6oKUcEayeFdIo_L3zZZ5LYUr2nnlkeEXi1KuhVbV_UE7JrmpsaMNoHEqmkJtzJB6yjQgqf77y6waWhKG-SBMgvMKG_8d9y5nUV5IiaxajGimiN0sek4xqhs3KxbUYbI0ejlUSlmPYEM"
    )

    audio_features = data_fetcher.fetch_audio_features(tracks)
    lyrics = data_fetcher.fetch_lyrics(tracks)
    print(audio_features)
    print(lyrics) """
