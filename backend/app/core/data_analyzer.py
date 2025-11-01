import polars as pl
from app.analyzers import TransformerAnalyzer


class DataAnalyzer:
    def __init__(self):
        pass

    def average_audio_features(self, tracks_audio_features: dict):
        n_tracks = len(tracks_audio_features)
        audio_features_df = pl.DataFrame(tracks_audio_features)

        numeric_cols = [
            "Energy",
            "Danceability",
            "Loudness",
            "Liveness",
            "Valence",
            "Acousticness",
            "Speechiness",
            "Popularity",
        ]

        avg_dict = audio_features_df.select(numeric_cols).mean().to_dicts()[0]
        return {
            "tracks": f"{n_tracks}/50",
            "average_audio_features": avg_dict,
        }

    def analyze_lyrics(self, tracks_lyrics):
        lyrics_analyzer = TransformerAnalyzer()
        tracks_scores = []
        emotions = {}
        n_tracks = len(tracks_lyrics)

        for track in tracks_lyrics:
            lyrics = track["Lyrics"]
            distribution = lyrics_analyzer.analyze(lyric=lyrics)["distribution"]

            for emotion, value in distribution.items():
                if emotion not in emotions:
                    emotions[emotion] = 0
                emotions[emotion] += value

        if n_tracks > 0:
            overall_average = {
                emotion: total / n_tracks for emotion, total in emotions.items()
            }
        else:
            overall_average = {}

        return {
            "tracks": f"{n_tracks}/50",
            "average_lyrics_inference": overall_average,
        }


# Test unitario
""" if __name__ == "__main__":
    from app.core import DataFetcher

    data_fetcher = DataFetcher()
    user_token = "BQBHJRls68SWjoVwe6EAlO-WzO7zKUH_FcLGZU14FA5mj3IDEdLy-N7YskF0LMKvVd1JToMxd9ZSW4b-z2krZoIL2RHNs2LsynR4Ke3HOzP0EbggrUxO2rOd2CPZ5YvPvJwxESRG8KtAB6TDXAjv13B_Iz0LrwgYOLtY4aR3eLHZlSZ8P-uxiKTBHE0N6LKA4KxXgBNzNq8VJwE2hTgxpjg3_7IpALT2gN67-8ht5Vv1Qtyrwz9NeKM_MYo7Cl4l"
    tracks = data_fetcher.fetch_recent_tracks(access_token=user_token)
    tracks_audio_features = data_fetcher.fetch_audio_features(tracks)
    tracks_lyrics = data_fetcher.fetch_lyrics(tracks)

    data_analyzer = DataAnalyzer()

    average_audio_features = data_analyzer.average_audio_features(tracks_audio_features)
    average_lyrics_inference_emotions = data_analyzer.analyze_lyrics(tracks_lyrics)

    print(
        f"[AVERAGE AUDIO FEATURES]: {average_audio_features}\n[LYRICS INFERENCE]: {average_lyrics_inference_emotions}"
    )
 """