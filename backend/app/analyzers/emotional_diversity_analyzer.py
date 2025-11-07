import numpy as np
from typing import Dict, List, Any
import matplotlib.pyplot as plt

class EmotionalDiversityAnalyzer:
    def __init__(self):
        # Categorías con solo nombre y color
        self.categories = {
            'high_valence_high_arousal': {'label': 'Alegría/Excitación', 'color': '#2ecc71'},
            'low_valence_high_arousal': {'label': 'Tensión/Ansiedad', 'color': '#e74c3c'},
            'low_valence_low_arousal': {'label': 'Tristeza/Melancolía', 'color': '#3498db'},
            'high_valence_low_arousal': {'label': 'Calma/Paz', 'color': '#f39c12'}
        }
    
    def _categorize_song(self, valence: float, arousal: float) -> str:
        if valence >= 50 and arousal >= 50:
            return 'high_valence_high_arousal'
        elif valence < 50 and arousal >= 50:
            return 'low_valence_high_arousal'
        elif valence < 50 and arousal < 50:
            return 'low_valence_low_arousal'
        else:
            return 'high_valence_low_arousal'

    def calculate_shannon_diversity(self, proportions: List[float]) -> float:
        shannon_index = -sum(p * np.log(p) for p in proportions if p > 0)
        return shannon_index

    def normalize_shannon_index(self, shannon_index: float, num_categories: int) -> float:
        max_shannon = np.log(num_categories)
        return shannon_index / max_shannon if max_shannon != 0 else 0

    def calculate_diversity_from_valence_arousal(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        songs = analysis_result['songs']
        category_counts = {c: 0 for c in self.categories}
        for song in songs:
            category = self._categorize_song(song['valence'], song['arousal'])
            category_counts[category] += 1

        total = len(songs)
        proportions = [count / total for count in category_counts.values()]
        shannon = self.calculate_shannon_diversity(proportions)
        normalized = self.normalize_shannon_index(shannon, len(self.categories))

        return {
            'shannon': shannon,
            'normalized': normalized,
            'category_counts': category_counts
        }

    def visualize(self, diversity_result: Dict[str, Any], save_path: str = None):
        fig = plt.figure(figsize=(12, 6))
        gs = fig.add_gridspec(1, 2, wspace=0.3)

        # Panel 1: Gráfico de pastel
        ax_pie = fig.add_subplot(gs[0, 0])
        counts = diversity_result['category_counts']
        labels = []
        sizes = []
        colors = []

        for cat, count in counts.items():
            if count > 0:
                labels.append(f"{self.categories[cat]['label']}\n{(count / sum(counts.values()))*100:.1f}%")
                sizes.append(count)
                colors.append(self.categories[cat]['color'])

        wedges, _, autotexts = ax_pie.pie(
            sizes, labels=labels, colors=colors,
            autopct='%d', startangle=90, textprops={'fontsize': 10, 'weight': 'bold'}
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
        ax_pie.set_title('Distribución de Categorías Emocionales', fontsize=14, fontweight='bold')

        # Panel 2: Medidor del índice de diversidad
        ax_gauge = fig.add_subplot(gs[0, 1])
        ax_gauge.axis('off')
        diversity_index = diversity_result['normalized']

        theta = np.linspace(0, np.pi, 100)
        radius = 1
        ax_gauge.plot(radius * np.cos(theta), radius * np.sin(theta), 'lightgray', linewidth=15)
        progress_theta = np.linspace(0, diversity_index * np.pi, 100)

        # Color según el nivel
        if diversity_index >= 0.85:
            color = '#2ecc71'
        elif diversity_index >= 0.65:
            color = '#27ae60'
        elif diversity_index >= 0.40:
            color = '#f39c12'
        else:
            color = '#e74c3c'

        ax_gauge.plot(radius * np.cos(progress_theta), radius * np.sin(progress_theta), color, linewidth=15)
        ax_gauge.text(0, 0.2, f'{diversity_index:.2f}', ha='center', va='center', fontsize=48, fontweight='bold', color=color)
        ax_gauge.text(0, -0.15, 'Índice de Diversidad', ha='center', va='center', fontsize=14, fontweight='bold')
        ax_gauge.text(-1.15, 0, '0.0', ha='right', va='center', fontsize=10)
        ax_gauge.text(1.15, 0, '1.0', ha='left', va='center', fontsize=10)
        ax_gauge.text(0, 1.15, '0.5', ha='center', va='bottom', fontsize=10)
        ax_gauge.set_xlim(-1.3, 1.3)
        ax_gauge.set_ylim(-0.3, 1.3)
        ax_gauge.set_aspect('equal')

        fig.suptitle('Análisis de Diversidad Emocional Musical', fontsize=18, fontweight='bold')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualización guardada en: {save_path}")

        plt.show()


def analyze_emotional_diversity(valence_arousal_result: Dict[str, Any]) -> Dict[str, Any]:
    analyzer = EmotionalDiversityAnalyzer()
    result = analyzer.calculate_diversity_from_valence_arousal(valence_arousal_result)
    analyzer.visualize(result)
    return result


if __name__ == "__main__":
    from app.analyzers import ValenceArousalAnalyzer
    from app.core import DataFetcher
    from app.analyzers import TransformerAnalyzer

    data_fetcher = DataFetcher()
    analyzer = ValenceArousalAnalyzer()
    transformer = TransformerAnalyzer()

    token = "BQCQ3vBM-yM-nW9SBlUewMI43YE50a7Z1CXVRKqTT_YMwnfg2Mu9m4zsAxwxcLIyWTREfEdYcvrhl3r5eAHyGoOvsclywN6qhLsSixi_W2rAnJ4ttFA4gzHnPdCBV66QFMOVqS7SYBnRt6QMZnWmtnlY3S2GywHrvRndu1ko7QETSXPS53ML8ZFBRHs-75mBejCVqvuW6GruVLFDuK9ACroVUKpcduRI_RJxGk6Q37lpTfJvnTnsG-aY17ivmvUS"
    songs = data_fetcher.fetch_recent_tracks(token)
    audio_features = data_fetcher.fetch_audio_features(songs)
    lyrics = data_fetcher.fetch_lyrics(songs)

    sentiment_data = [transformer.analyze(song_lyric) for song_lyric in lyrics]
    
    result = analyzer.process_songs(audio_features, sentiment_data)

    res = analyze_emotional_diversity(result)
    print(res)
    