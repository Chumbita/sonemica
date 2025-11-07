from app.core import DataFetcher
from app.core import DataAnalyzer
from app.analyzers import ValenceArousalAnalyzer
from app.analyzers import TransformerAnalyzer
from app.analyzers import graficar_paisaje_emocional
from app.analyzers import analyze_emotional_diversity

def main_flow(access_token):
  # Instanciamos las clases
  data_fetcher = DataFetcher()
  data_analyzer = DataAnalyzer()
  valence_arousal_analyzer = ValenceArousalAnalyzer()
  transformer_analyzer = TransformerAnalyzer()

  # Obtenemos las últimas 50 canciones escuchadas por el usuario
  user_songs = data_fetcher.fetch_recent_tracks(access_token)

  # b
  songs_with_audio_features = data_fetcher.fetch_audio_features(user_songs)

  # Letras
  songs_with_lyrics = data_fetcher.fetch_lyrics(user_songs)

  # Inferimos emociones sobre las letras encontradas
  songs_lyrics_emotional_inference = [transformer_analyzer.analyze(song) for song in songs_with_lyrics]

  # Análisis 
  avg_songs_audio_feautre = data_analyzer.average_audio_features(songs_with_audio_features)
  avg_songs_lyrics = data_analyzer.analyze_lyrics(songs_with_lyrics)

  # (1) Realizamos análisis de dimensiones Valence y Arousal
  valence_arousal_result = valence_arousal_analyzer.process_songs(songs_with_audio_features, songs_lyrics_emotional_inference) 

  # (2) Dudoso
  emotional_diversity_result = analyze_emotional_diversity(valence_arousal_result)

  # (3) Representación artística de las emociones.
  grafico_descripcion = graficar_paisaje_emocional(avg_songs_audio_feautre, avg_songs_lyrics)

  return {
    "valence_arousal_analysis": valence_arousal_result,
    "graphic_diversity_analysis": emotional_diversity_result,
    "graphic_description": grafico_descripcion,
  }


""" if __name__ == "__main__":
  access_token = "BQDDS96pO5i0HYrAU_sqmEkGGoefMn2h3PP9S1ZU8C2MHCd5mZZCN1UjqmSvmURIkEGounkfqtrVzwplEOa9zKp7dH4Q6Lb0-5oKV8umytb9-eebiBGH9T6S3dNONqtfJgL8pdB8VF0kZmGq6pZqD9MdOyFrtfoPGortBGwhozm3NA1ponDeMumT7uOItwTPFiOBSoA8j0huKWnD7BAImySnwN2K58sv4NPR2XUSoWEPPY0bk8dnDGH8zSiUK04p"
  main_flow(access_token) """