import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class BaseAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, lyric: str) -> dict:
        scores = self.analyzer.polarity_scores(lyric)
        return {
            "method": "base",
            "sentiment": (
                "positive"
                if scores["compound"] > 0.05
                else "negative" if scores["compound"] < -0.05 else "neutral"
            ),
            "confidence": abs(scores["compound"]),
            "raw": scores
        }

"""
Prueba unitaria de modelo de inferencia emocional
"""
if __name__ == "__main__":
    lyrics = "Tal vez parece que me pierdo en el camino, pero me guía la intuición. Nada me importa más que hacer el recorrido, más que saber adonde voy. No trates de persuadirme, voy a seguir en esto. Sé, nunca falla, hoy, el viento sopla a mi favor, voy a seguir haciéndolo. Las cosas brillantes siempre salen de repente, como la geometría de una flor. ¡Oh! Es la palabra antes que tus labios la suelten, sin secretos no hay amor. Todo me sirve, nada se pierde, yo lo transformo. Sé, nunca falla, el universo está mi favor, y es tan mágico. Voy a seguir haciéndolo. Me sirve cualquier pretexto, cualquier excusa, cualquier error. ¡Oh! ¡Oh! ¡Oh! (todo conspira a mi favor) Mágico, mágico."
    model = BaseAnalyzer()
    result = model.analyze(lyrics)
    print(result)
