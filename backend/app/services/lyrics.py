""" No implementar este servicio """
import requests
import re
from ftfy import fix_text
from urllib.parse import quote


class LyricsService:
    BASE_URL = "https://api.lyrics.ovh/v1"
    FALLBACK_URL = "https://lrclib.net/api/get"

    @staticmethod
    def _clean_lyrics(lyrics: str) -> str:
        if not lyrics:
            return None

        # Corrección de codificación
        lyrics = fix_text(lyrics)

        # Limpieza general
        lyrics = lyrics.strip()
        lyrics = lyrics.replace("\n", " ").replace("\r", " ")
        lyrics = re.sub(r"\s+", " ", lyrics)
        return lyrics

    @staticmethod
    def get_lyrics(artist: str, title: str) -> str:
        """
        Obtiene la letra de una canción usando la API pública de Lyrics.ovh.
        """

        artist_q = artist.strip()
        title_q = title.strip()

        try:
            url = f"{LyricsService.BASE_URL}/{quote(artist_q)}/{quote(title_q)}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            lyrics = data.get("lyrics")
            if lyrics:
                return LyricsService._clean_lyrics(lyrics)
        except requests.exceptions.RequestException as e:
            print(f"[Lyrics.ovh] Error for {artist_q} - {title_q}: {e}")

        return None


"""
Prueba unitaria de servicio 
"""

if __name__ == "__main__":
    service = LyricsService()
    artist = "Evanescence"
    title = "My Immortal"
    lyrics = service.get_lyrics(artist, title)
    if lyrics:
        print(f"Lyrics for '{title}' by {artist}:\n{lyrics}")
    else:
        print(f"Lyrics for '{title}' by {artist} not found.")
