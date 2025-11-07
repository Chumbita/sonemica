import numpy as np
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import json

class EmotionalDiversityAnalyzer:
    """
    Analizador de diversidad emocional basado en el índice de Shannon.
    """
    
    def __init__(self):
        # Definimos las cuatro categorías principales del modelo circumplejo. Cada una representa una región del espacio emocional bidimensional
        self.categories = {
            'high_valence_high_arousal': {
                'label': 'Alegría/Excitación',
                'description': 'Emociones positivas y energéticas',
                'color': '#2ecc71',  # Verde vibrante
                'emoji': '😄'
            },
            'low_valence_high_arousal': {
                'label': 'Tensión/Ansiedad',
                'description': 'Emociones activadas pero negativas',
                'color': '#e74c3c',  # Rojo
                'emoji': '😰'
            },
            'low_valence_low_arousal': {
                'label': 'Tristeza/Melancolía',
                'description': 'Emociones desactivadas y negativas',
                'color': '#3498db',  # Azul
                'emoji': '😢'
            },
            'high_valence_low_arousal': {
                'label': 'Calma/Paz',
                'description': 'Emociones relajadas y positivas',
                'color': '#f39c12',  # Amarillo/naranja
                'emoji': '😌'
            }
        }
    
    def _categorize_song(self, valence: float, arousal: float) -> str:
        """
        Categoriza una canción en uno de los cuatro cuadrantes emocionales.
        """
        if valence >= 50 and arousal >= 50:
            return 'high_valence_high_arousal'
        elif valence < 50 and arousal >= 50:
            return 'low_valence_high_arousal'
        elif valence < 50 and arousal < 50:
            return 'low_valence_low_arousal'
        else:  # valence >= 50 and arousal < 50
            return 'high_valence_low_arousal'
    
    def calculate_shannon_diversity(self, proportions: List[float]) -> float:
        """
        Calcula el índice de diversidad de Shannon.
        
        El índice de Shannon mide tanto la riqueza (número de categorías presentes)
        como la equidad (qué tan balanceada está la distribución). La fórmula es:
        H = -Σ(p_i * ln(p_i))
        
        donde p_i es la proporción de elementos en la categoría i.
        
        Un índice más alto indica mayor diversidad. El valor va de 0 (toda la música
        en una sola categoría) hasta ln(n) donde n es el número de categorías posibles.
        """
        shannon_index = 0
        
        for proportion in proportions:
            # Solo incluimos categorías que tienen al menos algo
            # El logaritmo de cero no está definido, así que saltamos proporciones de cero
            if proportion > 0:
                # La fórmula: -p * ln(p)
                # El logaritmo natural de una proporción pequeña es un número negativo grande
                # Multiplicado por la proporción y con signo negativo, contribuye positivamente
                shannon_index += proportion * np.log(proportion)
        
        # Aplicamos el signo negativo para obtener el valor positivo final
        return -shannon_index
    
    def normalize_shannon_index(self, shannon_index: float, num_categories: int) -> float:
        """
        Normaliza el índice de Shannon a una escala de 0 a 1.
        
        El índice de Shannon sin normalizar puede ir de 0 hasta ln(n) donde n es
        el número de categorías. Para hacer el índice más interpretable, lo dividimos
        por su valor máximo posible, resultando en una escala de 0 a 1.
        
        Un valor de 0 significa diversidad nula (todo en una categoría).
        Un valor de 1 significa diversidad máxima (distribución perfectamente uniforme).
        
        Args:
            shannon_index: El índice de Shannon calculado
            num_categories: Número de categorías posibles
            
        Returns:
            Índice normalizado entre 0 y 1
        """
        # El máximo valor posible del índice de Shannon ocurre cuando todas las
        # categorías tienen exactamente la misma proporción (distribución uniforme)
        max_shannon = np.log(num_categories)
        
        # Evitamos división por cero en el caso extremo de una sola categoría
        if max_shannon == 0:
            return 0
        
        # Normalizamos dividiendo por el máximo posible
        return shannon_index / max_shannon
    
    def calculate_diversity_from_valence_arousal(
        self, 
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula el índice de diversidad emocional a partir del análisis de valencia-arousal.
        
        Esta es la función principal que orquesta todo el análisis de diversidad.
        Toma el resultado del análisis de valencia-arousal que ya implementaste
        y calcula las métricas de diversidad emocional.
        
        Args:
            analysis_result: El diccionario resultado de ValenceArousalAnalyzer.process_songs()
            
        Returns:
            Diccionario con el índice de diversidad y toda la información contextual
        """
        songs = analysis_result['songs']
        
        # Contamos cuántas canciones caen en cada categoría emocional
        category_counts = {category: 0 for category in self.categories.keys()}
        
        # También vamos a guardar qué canciones específicas están en cada categoría
        # Esto será útil para dar ejemplos al usuario
        songs_by_category = {category: [] for category in self.categories.keys()}
        
        for song in songs:
            valence = song['valence']
            arousal = song['arousal']
            
            # Determinamos a qué categoría pertenece esta canción
            category = self._categorize_song(valence, arousal)
            
            # Incrementamos el contador para esa categoría
            category_counts[category] += 1
            
            # Guardamos la información de la canción
            songs_by_category[category].append({
                'title': song['title'],
                'artist': song['artist'],
                'valence': valence,
                'arousal': arousal
            })
        
        total_songs = len(songs)
        
        # Calculamos las proporciones de cada categoría
        proportions = [count / total_songs for count in category_counts.values()]
        
        # Calculamos el índice de Shannon
        shannon_index = self.calculate_shannon_diversity(proportions)
        
        # Normalizamos el índice a escala 0-1
        num_categories = len(self.categories)
        normalized_diversity = self.normalize_shannon_index(shannon_index, num_categories)
        
        # Determinamos cuántas categorías están presentes (tienen al menos una canción)
        categories_present = sum(1 for count in category_counts.values() if count > 0)
        
        # Calculamos qué porcentaje representa cada categoría
        category_percentages = {}
        for category, count in category_counts.items():
            category_percentages[category] = {
                'count': count,
                'percentage': round((count / total_songs) * 100, 2),
                'label': self.categories[category]['label'],
                'description': self.categories[category]['description'],
                'sample_songs': songs_by_category[category][:3]  # Primeras 3 canciones como ejemplo
            }
        
        # Identificamos la categoría dominante (la que tiene más canciones)
        dominant_category = max(category_counts, key=category_counts.get)
        dominant_percentage = (category_counts[dominant_category] / total_songs) * 100
        
        # Generamos una interpretación cualitativa del índice
        interpretation = self._interpret_diversity_index(
            normalized_diversity, 
            categories_present,
            dominant_category,
            dominant_percentage
        )
        
        # Estructura del resultado
        diversity_result = {
            'diversity_index': {
                'raw_shannon': round(shannon_index, 4),
                'normalized': round(normalized_diversity, 4),
                'scale': '0 (nula) a 1 (máxima)',
                'interpretation': interpretation
            },
            'category_distribution': category_percentages,
            'summary': {
                'total_songs': total_songs,
                'categories_present': categories_present,
                'categories_possible': num_categories,
                'dominant_category': {
                    'category': dominant_category,
                    'label': self.categories[dominant_category]['label'],
                    'percentage': round(dominant_percentage, 2)
                }
            },
            'metadata': {
                'method': 'Shannon Diversity Index',
                'based_on': 'Circumplex Model of Affect (Valence-Arousal)',
                'categories_used': list(self.categories.keys())
            }
        }
        
        return diversity_result
    
    def _interpret_diversity_index(
        self, 
        normalized_diversity: float,
        categories_present: int,
        dominant_category: str,
        dominant_percentage: float
    ) -> Dict[str, str]:
        """
        Genera una interpretación cualitativa del índice de diversidad.
        
        Esta función traduce el número abstracto del índice en lenguaje
        comprensible y significativo para el usuario, contextualizando
        qué significa ese valor en términos de su bienestar emocional.
        
        Args:
            normalized_diversity: Índice de diversidad normalizado (0-1)
            categories_present: Número de categorías emocionales presentes
            dominant_category: La categoría con más canciones
            dominant_percentage: Porcentaje de la categoría dominante
            
        Returns:
            Diccionario con nivel, título, descripción y recomendación
        """
        # Determinamos el nivel de diversidad basándonos en umbrales investigados
        # Estos umbrales están inspirados en la investigación de Quoidbach et al.
        if normalized_diversity >= 0.85:
            level = 'muy_alta'
            title = 'Diversidad Emocional Excepcional'
            description = (
                f"Tu índice de diversidad de {normalized_diversity:.2f} es excepcionalmente alto. "
                f"Has navegado fluidamente entre {categories_present} estados emocionales diferentes, "
                f"mostrando una paleta emocional rica y variada. Esta capacidad de experimentar "
                f"y transitar entre diferentes emociones a través de la música se asocia con "
                f"flexibilidad psicológica y resiliencia emocional. Estás aprovechando todo el "
                f"espectro de experiencias emocionales que la música puede ofrecer."
            )
            recommendation = (
                "Continúa explorando esta variedad emocional. Tu apertura a diferentes "
                "estados emocionales es una fortaleza. Considera reflexionar sobre cómo "
                "diferentes tipos de música te ayudan en diferentes situaciones o momentos del día."
            )
            
        elif normalized_diversity >= 0.65:
            level = 'alta'
            title = 'Buena Diversidad Emocional'
            description = (
                f"Tu índice de diversidad de {normalized_diversity:.2f} indica una buena variedad "
                f"emocional. Has explorado {categories_present} categorías emocionales, mostrando "
                f"flexibilidad en tu selección musical. Aunque hay cierta predominancia de "
                f"{self.categories[dominant_category]['label'].lower()} ({dominant_percentage:.0f}% de tu música), "
                f"aún mantienes un equilibrio saludable con otras emociones. Esta diversidad "
                f"sugiere que estás usando la música de manera adaptativa para diferentes necesidades."
            )
            recommendation = (
                "Tu diversidad emocional es saludable. Si quisieras expandir aún más tu paleta, "
                "podrías experimentar conscientemente con música de las categorías menos "
                "representadas en tu selección actual."
            )
            
        elif normalized_diversity >= 0.40:
            level = 'moderada'
            title = 'Diversidad Emocional Moderada'
            description = (
                f"Tu índice de diversidad de {normalized_diversity:.2f} está en un rango moderado. "
                f"Tu música se concentra bastante en {self.categories[dominant_category]['label'].lower()} "
                f"({dominant_percentage:.0f}% de tus canciones), con presencia de {categories_present} "
                f"categorías en total. Esta concentración no es necesariamente negativa, podría "
                f"reflejar que estás procesando intensamente un estado emocional particular o "
                f"que tienes una preferencia fuerte por cierto tipo de música."
            )
            recommendation = (
                "Considera si esta concentración emocional es intencional o si te beneficiarías "
                "de mayor variedad. Experimentar con música que exprese otras emociones podría "
                "ayudarte a acceder a diferentes estados mentales y ampliar tu flexibilidad emocional. "
                "La investigación sugiere que mayor emodiversidad se correlaciona con mejor bienestar."
            )
            
        else:  # < 0.40
            level = 'baja'
            title = 'Diversidad Emocional Limitada'
            description = (
                f"Tu índice de diversidad de {normalized_diversity:.2f} indica una concentración "
                f"emocional bastante marcada. Una proporción muy alta de tu música ({dominant_percentage:.0f}%) "
                f"cae en la categoría de {self.categories[dominant_category]['label'].lower()}, "
                f"con solo {categories_present} categorías representadas. Esta homogeneidad podría "
                f"sugerir que estás sumergido en un estado emocional específico, lo cual está "
                f"perfectamente bien ocasionalmente, especialmente cuando estás procesando algo importante."
            )
            recommendation = (
                "Si este patrón se repite frecuentemente, podría valer la pena explorar "
                "conscientemente una mayor variedad emocional en tu música. La investigación "
                "en psicología emocional muestra que las personas con mayor emodiversidad "
                "tienden a tener mejor salud mental y mayor capacidad de regulación emocional. "
                "Podrías experimentar creando playlists que incluyan intencionalmente diferentes "
                "tipos de emociones y observar cómo te sientes."
            )
        
        return {
            'level': level,
            'title': title,
            'description': description,
            'recommendation': recommendation
        }
    
    def visualize(
        self, 
        diversity_result: Dict[str, Any],
        save_path: str = None
    ):
        """
        Crea una visualización comprehensiva del análisis de diversidad emocional.
        
        Esta visualización incluye un gráfico de pastel que muestra la distribución
        entre categorías, el índice numérico prominente, y texto explicativo.
        
        Args:
            diversity_result: El resultado de calculate_diversity_from_valence_arousal()
            save_path: Ruta opcional para guardar la imagen
        """
        fig = plt.figure(figsize=(16, 10))
        
        # Creamos una cuadrícula para organizar los diferentes elementos
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Panel 1: Gráfico de pastel con la distribución de categorías
        ax_pie = fig.add_subplot(gs[0:2, 0])
        
        category_dist = diversity_result['category_distribution']
        
        # Extraemos los datos para el gráfico de pastel
        labels = []
        sizes = []
        colors = []
        
        for category, data in category_dist.items():
            if data['count'] > 0:  # Solo incluimos categorías presentes
                labels.append(f"{data['label']}\n{data['percentage']:.1f}%")
                sizes.append(data['count'])
                colors.append(self.categories[category]['color'])
        
        # Creamos el gráfico de pastel
        wedges, texts, autotexts = ax_pie.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%d',  # Muestra el conteo
            startangle=90,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        # Mejoramos la legibilidad de los textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(13)
            autotext.set_weight('bold')
        
        ax_pie.set_title(
            'Distribución de Categorías Emocionales',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        
        # Panel 2: Medidor del índice de diversidad
        ax_gauge = fig.add_subplot(gs[0, 1])
        ax_gauge.axis('off')
        
        diversity_index = diversity_result['diversity_index']['normalized']
        interpretation = diversity_result['diversity_index']['interpretation']
        
        # Creamos un medidor visual estilo semicírculo
        # Dibujamos el arco de fondo
        theta = np.linspace(0, np.pi, 100)
        radius = 1
        
        # Arco de fondo (gris)
        ax_gauge.plot(
            radius * np.cos(theta),
            radius * np.sin(theta),
            'lightgray',
            linewidth=15
        )
        
        # Arco de progreso (colorizado según el nivel)
        progress_theta = np.linspace(0, diversity_index * np.pi, 100)
        
        # Color según el nivel de diversidad
        if diversity_index >= 0.85:
            progress_color = '#2ecc71'  # Verde
        elif diversity_index >= 0.65:
            progress_color = '#27ae60'  # Verde oscuro
        elif diversity_index >= 0.40:
            progress_color = '#f39c12'  # Naranja
        else:
            progress_color = '#e74c3c'  # Rojo
        
        ax_gauge.plot(
            radius * np.cos(progress_theta),
            radius * np.sin(progress_theta),
            progress_color,
            linewidth=15
        )
        
        # Añadimos el valor numérico en el centro
        ax_gauge.text(
            0, 0.2,
            f'{diversity_index:.2f}',
            ha='center',
            va='center',
            fontsize=48,
            fontweight='bold',
            color=progress_color
        )
        
        ax_gauge.text(
            0, -0.15,
            'Índice de Diversidad',
            ha='center',
            va='center',
            fontsize=14,
            fontweight='bold'
        )
        
        # Marcas en el medidor
        ax_gauge.text(-1.15, 0, '0.0', ha='right', va='center', fontsize=10)
        ax_gauge.text(1.15, 0, '1.0', ha='left', va='center', fontsize=10)
        ax_gauge.text(0, 1.15, '0.5', ha='center', va='bottom', fontsize=10)
        
        ax_gauge.set_xlim(-1.3, 1.3)
        ax_gauge.set_ylim(-0.3, 1.3)
        ax_gauge.set_aspect('equal')
        
        # Panel 3: Interpretación textual
        ax_interpretation = fig.add_subplot(gs[1, 1])
        ax_interpretation.axis('off')
        
        interpretation_text = (
            f"{interpretation['title']}\n\n"
            f"{interpretation['description'][:300]}..."
        )
        
        ax_interpretation.text(
            0.05, 0.95,
            interpretation_text,
            transform=ax_interpretation.transAxes,
            fontsize=10,
            verticalalignment='top',
            wrap=True,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5, pad=15)
        )
        
        # Panel 4: Estadísticas resumidas
        ax_stats = fig.add_subplot(gs[2, :])
        ax_stats.axis('off')
        
        summary = diversity_result['summary']
        dominant = summary['dominant_category']
        
        stats_text = (
            f"📊 Resumen Estadístico:\n\n"
            f"• Total de canciones analizadas: {summary['total_songs']}\n"
            f"• Categorías emocionales presentes: {summary['categories_present']} de {summary['categories_possible']}\n"
            f"• Categoría dominante: {dominant['label']} ({dominant['percentage']:.1f}% de tu música)\n"
            f"• Índice de Shannon (sin normalizar): {diversity_result['diversity_index']['raw_shannon']:.4f}\n\n"
            f"💡 Recomendación:\n{interpretation['recommendation']}"
        )
        
        ax_stats.text(
            0.05, 0.95,
            stats_text,
            transform=ax_stats.transAxes,
            fontsize=11,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3, pad=20)
        )
        
        # Título general
        fig.suptitle(
            'Análisis de Diversidad Emocional Musical',
            fontsize=18,
            fontweight='bold',
            y=0.98
        )
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualización guardada en: {save_path}")
        
        # plt.show()


# Función auxiliar para usar directamente con el resultado de valencia-arousal
def analyze_emotional_diversity(
    valence_arousal_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Función wrapper para analizar diversidad emocional desde un análisis de valencia-arousal.
    
    Args:
        valence_arousal_result: Resultado de ValenceArousalAnalyzer.process_songs()
        
    Returns:
        Diccionario con el análisis completo de diversidad emocional
    """
    analyzer = EmotionalDiversityAnalyzer()
    diversity_result = analyzer.calculate_diversity_from_valence_arousal(valence_arousal_result)

    analyzer.visualize(diversity_result, ".")
    return diversity_result

if __name__ == "__main__":
    from app.analyzers import ValenceArousalAnalyzer
    from app.core import DataFetcher
    from app.analyzers import TransformerAnalyzer

    data_fetcher = DataFetcher()
    analyzer = ValenceArousalAnalyzer()
    transformer = TransformerAnalyzer()

    token = "BQBXv_ziSckDzCksUaz_uVWB2TVwhawavK2gCAwFIM7V6qDYc9lEH-ZqyE77r1JUQxOSX-WTUdwHMiENp8OVDjn19Yi_cdTyL9styr6w7pVkhJZLmUhlQbbnYbzDsmf2UkWP-PyhriRscm03G9ZfoyVpqMEaakeXlQ6DEdRJU31htKMkGu5hTpqm6BNHq7Pokexo9bfr5nB2EKnB2aJ9EDqlxUP1eKQQ0jakyjJYn01CgK5kT56Zxt4u_zV9nOKr"
    songs = data_fetcher.fetch_recent_tracks(token)
    audio_features = data_fetcher.fetch_audio_features(songs)
    lyrics = data_fetcher.fetch_lyrics(songs)

    sentiment_data = [transformer.analyze(song_lyric) for song_lyric in lyrics]
    
    result = analyzer.process_songs(audio_features, sentiment_data)

    res = analyze_emotional_diversity(result)
    print(res)
    