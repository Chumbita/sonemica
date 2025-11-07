import polars as pl
import numpy as np
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import json
import re
from difflib import SequenceMatcher


class ValenceArousalAnalyzer:
    def __init__(
        self, weight_music_valence: float = 0.6, weight_lyrics_valence: float = 0.4
    ):
        self.weight_music_valence = weight_music_valence
        self.weight_lyrics_valence = weight_lyrics_valence

    # Métodos auxiliares
    def _normalize_string(self, text: str) -> str:
        """
        Función auxiliar para normalizar strings para hacer búsquedas entre audio features y lyrics
        """

        if not text:
            return ""

        # Convertimos a minúsculas
        text = text.lower()

        # Removemos caracteres especiales y puntuación
        text = re.sub(r"[^a-z0-9]", "", text)

        return text

    def _create_song_key(self, title: str, artist: str) -> str:
        """
        Crea una clave única normalizada para una canción.
        """

        normalized_title = self._normalize_string(title)
        normalized_artist = self._normalize_string(artist)
        return f"{normalized_title}|{normalized_artist}"

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calcula similitud entre dos strings usando el algoritmo de Ratcliff/Obsershelp.
        """

        return SequenceMatcher(None, str1, str2).ratio()

    def _find_matching_sentiment(
        self, song_key: str, sentiment_data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, float]]:
        """
        Busca el análisis de sentimientos de la letra correspondiente a una canción.
        Primero intante con una coincidencia exacta, si no encuentra nada busca una coincidencia por similitud.
        """
        if not sentiment_data:
            return None

        # Match exacto
        for sentiment in sentiment_data:
            sentiment_key = self._create_song_key(
                sentiment.get("title", ""), sentiment.get("artist", "")
            )
            if song_key == sentiment_key:
                return {
                    "joy": sentiment.get("joy", 0),
                    "sadness": sentiment.get("sadness", 0),
                    "optimism": sentiment.get("optimism", 0),
                    "anger": sentiment.get("anger", 0),
                }

        # Si no hay match exacto, buscamos por similitud
        best_match = None
        best_similarity = 0

        for sentiment in sentiment_data:
            sentiment_key = self._create_song_key(
                sentiment.get("title", ""), sentiment.get("artist", "")
            )

            similarity = self._calculate_similarity(song_key, sentiment_key)

            if similarity > best_similarity and similarity >= 0.85:
                best_similarity = similarity
                best_match = {
                    "joy": sentiment.get("joy", 0),
                    "sadness": sentiment.get("sadness", 0),
                    "optimism": sentiment.get("optimism", 0),
                    "anger": sentiment.get("anger", 0),
                }

        return best_match

    def _classify_emotional_state(
        self, valence: float, arousal: float
    ) -> Dict[str, str]:
        """
        Clasifica el estado emocional basado en valencia y arousal
        """

        if valence >= 50 and arousal >= 50:
            category = "high_valence_high_arousal"
            label = "Alegría/Excitación"
            description = "Estado enérgico y positivo"
        elif valence < 50 and arousal >= 50:
            category = "low_valence_high_arousal"
            label = "Tensión/Ansiedad"
            description = "Estado activado pero negativo"
        elif valence < 50 and arousal < 50:
            category = "low_valence_low_arousal"
            label = "Tristeza/Melancolía"
            category = "Estado desactivado y negativo"
        else:
            category = "high_valence_low_arousal"
            label = "Calma/Paz"
            description = "Estado relajado y positivo"

        return {"category": category, "label": label, "description": description}

    def _calculate_quadrant_distribution(
        self, valences: np.ndarray, arousals: np.ndarray
    ) -> Dict[str, Any]:
        total = len(valences)

        q1 = np.sum((valences >= 50) & (arousals >= 50))
        q2 = np.sum((valences < 50) & (arousals >= 50))
        q3 = np.sum((valences < 50) & (arousals < 50))
        q4 = np.sum((valences >= 50) & (arousals < 50))

        return {
            "high_valence_high_arousal": {
                "count": int(q1),
                "percentage": round((q1 / total) * 100, 2),
                "label": "Alegría/Excitación",
            },
            "low_valence_high_arousal": {
                "count": int(q2),
                "percentage": round((q2 / total) * 100, 2),
                "label": "Tensión/Ansiedad",
            },
            "low_valence_low_arousal": {
                "count": int(q3),
                "percentage": round((q3 / total) * 100, 2),
                "label": "Tristeza/Melancolía",
            },
            "high_valence_low_arousal": {
                "count": int(q4),
                "percentage": round((q4 / total) * 100, 2),
                "label": "Calma/Paz",
            },
        }

    # Métodos principales
    def calculate_lyrics_valence(self, sentiment_scores: Dict[str, float]) -> float:
        """
        Convieete las puntuaciones de sentimientos en una valencia lírica.
        """

        # Extraemos las puntuaciones de cada emoción
        joy = sentiment_scores["distribution"].get("joy")
        optimism = sentiment_scores["distribution"].get("optimism")
        sadness = sentiment_scores["distribution"].get("sadness")
        anger = sentiment_scores["distribution"].get("anger")

        # Las emociones positivas suman, las negativas restan
        positive_contribution = (joy + optimism) * 100
        negative_contribution = (sadness + anger) * 100

        # Obtenemos la valencia lírica el cuál es la diferencia entre positivo y negativo
        lyrics_valence = 50 + (positive_contribution - negative_contribution) / 2

        return np.clip(lyrics_valence, 0, 100)

    def calculate_arousal(self, energy: float, loudness: float) -> float:
        """
        Calcula el arousal (nivel de activación) a partir de energía y volumen.
        """

        # Normalización de loudness: -60 será 0, y 0 será 100
        normalized_loudness = np.clip((loudness + 60) / 60 * 100, 0, 100)

        # Combinamos energía (80%) con loudness (20%)
        arousal = (energy * 0.8) + (normalized_loudness * 0.2)

        return np.clip(arousal, 0, 100)

    def process_songs(
        self,
        songs_data: List[Dict[str, Any]],
        sentiment_data: List[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Procesa la lista de canciones y calcula valencia y arousal para cada una.
        """

        processed_songs = []
        valences = []
        arousals = []

        # Estadísticas
        stats = {
            "total_input_songs": 50,
            "songs_with_audio_features": len(songs_data),
            "songs_with_sentiments": len(sentiment_data),
            "songs_with_both": 0,
            "songs_with_only_audio": 0,
            "songs_with_only_sentiments": 0,
            "songs_processed": 0,
            "songs_skipped": 0,
        }
        
        # Creamos un diccionario de audio features indexado por clave de canción
        audio_features_dict = {}
        if len(songs_data) > 0:
            for song in songs_data:
                title = song.get("Title")
                artist = song.get("Artist")
                if title and artist:
                    song_key = self._create_song_key(title, artist)
                    audio_features_dict[song_key] = song

        sentiment_dict = {}
        if len(sentiment_data) > 0:
            for sentiment in sentiment_data:
                title = sentiment.get("title")
                artist = sentiment.get("artist")
                if title and artist:
                    song_key = self._create_song_key(title, artist)
                    sentiment_dict[song_key] = sentiment

        # Obtenemos todas las claves únicas
        all_song_keys = set(audio_features_dict.keys()) | set(sentiment_dict.keys())

        # Procesamos cada canción
        for song_key in all_song_keys:
            audio_data = audio_features_dict.get(song_key)
            sentiment_data = sentiment_dict.get(song_key)

            if audio_data: 
                title = audio_data.get("Title")
                artist = audio_data.get("Artist")
            elif sentiment_data:
                title = sentiment_data.get("title")
                artist = sentiment_data.get("artist")
            else: 
                continue
            
        
            music_valence = None
            energy = None
            loudness = None

            if audio_data:
                music_valence = audio_data.get("Valence")
                energy = audio_data.get("Energy")
                loudness = audio_data.get("Loudness")
            
            # Calculamos Valence de la letra
            lyrics_valence = None
            if sentiment_data:
                lyrics_valence = self.calculate_lyrics_valence(sentiment_data)

            # Verificamos si tenemos por lo menos alguna fuente de valencia
            if music_valence is None and lyrics_valence is None:
                stats["songs_skipped"] += 1
                continue

            # Calculamos valencia 
            if music_valence is not None and lyrics_valence is not None:
                # Caso ideal: para esta canción hay audio feature y análisis emocional de la letra
                final_valence = (
                    music_valence * self.weight_music_valence
                    + lyrics_valence * self.weight_lyrics_valence
                )
                stats["songs_with_both"] += 1
                data_source = "both"
            
            elif music_valence is not None: 
                # Para esta canción solo hay audio feature
                final_valence = music_valence
                stats["songs_with_only_audio"] += 1
                data_source = "audio_only"
            
            else: 
                # Solo tenemos análisis emocional de la letra
                final_valence = lyrics_valence
                stats["songs_with_only_sentiments"] += 1
                data_source = "lyrics_only"

            if audio_data:
                arousal = self.calculate_arousal(energy, loudness)
            elif sentiment_data:
                anger = sentiment_data["distribution"].get("anger")
                joy = sentiment_data["distribution"].get("joy")
                sadness = sentiment_data["distribution"].get("sadness")
                optimism = sentiment_data["distribution"].get("optimism")

                estimated_arousal = 50 + (anger * 40) + (joy * 20) + (optimism * 15) - (sadness * 30)
                arousal = np.clip(estimated_arousal, 0, 100)
            else: 
                pass

            # Creamos el objeto de canción procesada
            song_processed = {
                "title": title,
                "artist": artist,
                "valence": round(final_valence, 2),
                "arousal": round(arousal, 2),
                "music_valence": (
                    round(music_valence, 2) if music_valence is not None else None
                ),
                "lyrics_valence": (
                    round(lyrics_valence, 2) if lyrics_valence is not None else None
                ),
                "energy": energy,
                "loudness": loudness,
                "data_source": data_source,
                "sentiment_scores": sentiment_data,
            }

            processed_songs.append(song_processed)
            valences.append(final_valence)
            arousals.append(arousal)
            stats["songs_processed"] += 1

        # Cálculo de estadísticas
        valences_array = np.array(valences)
        arousals_array = np.array(arousals)

        centroid_valence = float(np.mean(valences_array))
        centroid_arousal = float(np.mean(arousals_array))

        valence_std = float(np.std(valences_array))
        arousal_std = float(np.std(arousals_array))

        emotional_state = self._classify_emotional_state(centroid_valence, centroid_arousal)
        quadrant_distribution = self._calculate_quadrant_distribution(valences_array, arousals_array)

        result = {
            'songs': processed_songs,
            'summary': {
                'total_songs': len(processed_songs),
                'centroid': {
                    'valence': round(centroid_valence, 2),
                    'arousal': round(centroid_arousal, 2),
                    'emotional_state': emotional_state
                },
                'dispersion': {
                    'valence_std': round(valence_std, 2),
                    'arousal_std': round(arousal_std, 2)
                },
                'quadrant_distribution': quadrant_distribution
            },
            'stats': stats  
        }
        
        return result
    
    def visualize(self, analysis_result: Dict[str, Any], save_path: str = None):
        """
        Crea una visualización del análisis de Valencia-Arousal.
        
        Ahora incluye código de color para mostrar qué canciones tienen
        ambos tipos de datos vs solo uno.
        """
        if 'error' in analysis_result:
            print(f"Error: {analysis_result['error']}")
            return
        
        songs = analysis_result['songs']
        centroid = analysis_result['summary']['centroid']
        stats = analysis_result.get('stats', {})
        
        valences = [s['valence'] for s in songs]
        arousals = [s['arousal'] for s in songs]
        
        # Extraemos el tipo de fuente de datos para colorear los puntos
        data_sources = [s['data_source'] for s in songs]
        
        # Mapeamos fuentes de datos a colores
        color_map = {
            'both': 'darkblue',
            'audio_only': 'orange',
            'lyrics_only': 'green'
        }
        colors = [color_map[source] for source in data_sources]
        
        fig, ax = plt.subplots(figsize=(14, 11))
        
        # Dibujamos las líneas del cuadrante
        ax.axhline(y=50, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.axvline(x=50, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        
        # Coloreamos el fondo de cada cuadrante
        ax.fill_between([50, 100], 50, 100, alpha=0.1, color='green')
        ax.fill_between([0, 50], 50, 100, alpha=0.1, color='red')
        ax.fill_between([0, 50], 0, 50, alpha=0.1, color='blue')
        ax.fill_between([50, 100], 0, 50, alpha=0.1, color='yellow')
        
        # Graficamos cada canción con su color según la fuente de datos
        for i, (v, a, c) in enumerate(zip(valences, arousals, colors)):
            ax.scatter(v, a, c=c, s=100, alpha=0.6, edgecolors='black', linewidth=1)
        
        # Graficamos el centroide
        ax.scatter(centroid['valence'], centroid['arousal'],
                  c='red', s=300, marker='*', edgecolors='darkred',
                  linewidth=2, label='Centroide Emocional', zorder=5)
        
        # Etiquetamos algunas canciones extremas
        valence_sorted_idx = np.argsort(valences)
        arousal_sorted_idx = np.argsort(arousals)
        
        indices_to_label = set(
            list(valence_sorted_idx[:2]) + list(valence_sorted_idx[-2:]) +
            list(arousal_sorted_idx[:2]) + list(arousal_sorted_idx[-2:])
        )
        
        for idx in indices_to_label:
            song = songs[idx]
            ax.annotate(f"{song['title']}\n{song['artist']}", 
                       (valences[idx], arousals[idx]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8,
                       bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='white', edgecolor='gray', alpha=0.7))
        
        ax.set_xlabel('Valencia (Negativo → Positivo)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Arousal (Calmado → Excitado)', fontsize=12, fontweight='bold')
        ax.set_title('Mapa Emocional de tu Música\nModelo Valencia-Arousal', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
        
        # Texto informativo actualizado con estadísticas
        emotional_state = centroid['emotional_state']
        textstr = f"Tu centro emocional:\n{emotional_state['label']}\n{emotional_state['description']}\n\n"
        textstr += f"Canciones procesadas: {stats.get('songs_processed', 0)}\n"
        textstr += f"Con ambos datos: {stats.get('songs_with_both', 0)}\n"
        textstr += f"Solo audio: {stats.get('songs_with_only_audio', 0)}\n"
        textstr += f"Solo letras: {stats.get('songs_with_only_sentiments', 0)}"
        
        ax.text(0.02, 0.98, textstr,
               transform=ax.transAxes, fontsize=9,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Leyenda actualizada con los colores de fuente de datos
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='darkblue', label='Audio + Letras'),
            Patch(facecolor='orange', label='Solo Audio Features'),
            Patch(facecolor='green', label='Solo Análisis Letras'),
            ax.scatter([], [], c='red', s=300, marker='*', 
                      edgecolors='darkred', linewidth=2, label='Centroide')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualización guardada en: {save_path}")
        
        #plt.show()


if __name__ == "__main__": 
    from app.core import DataFetcher
    from app.analyzers import TransformerAnalyzer

    data_fetcher = DataFetcher()
    analyzer = ValenceArousalAnalyzer()
    transformer = TransformerAnalyzer()

    token = "BQCHNwcA2WjaaTj0bU0G1Icz4BDSlXoDmCi0wApON_bDloxjZE-4BF3Um_hcIzHSsDTnSR41umS5x-mWQO_rSzErmSsvypyR3oJfS3s7VB4_BZHijrJ0o1nkIsmEHhC3aMm-URHX9cTPKCNxgYGAyYKJUIREy8VFc_bSInHSIbzIAIIHjzIOqOIGd9mnjD91GIocSJjP0_sPQI89HA_qU89OVmRiuyy4LlyRUefLvmNXdxuuDb77H5Ng"
    songs = data_fetcher.fetch_recent_tracks(token)
    audio_features = data_fetcher.fetch_audio_features(songs)
    lyrics = data_fetcher.fetch_lyrics(songs)

    sentiment_data = [transformer.analyze(song_lyric) for song_lyric in lyrics]
    
    result = analyzer.process_songs(audio_features, sentiment_data)

    analyzer.visualize(result, ".")