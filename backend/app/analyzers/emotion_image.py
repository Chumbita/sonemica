import os
import requests
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from huggingface_hub import InferenceClient

# Cargar token Hugging Face
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY1")
IMGBB_TOKEN = os.getenv("IMGBB_API_KEY")

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

client = InferenceClient(
    provider="nebius",
    api_key = HF_TOKEN,
)


# 1 Generar prompt emocional 

def generar_prompt_emocional(distribucion):
    emotion_colors = {
        "anger": "rojos intensos, sombras oscuras, contrastes violentos, fuego, tormenta, rocas",
        "joy": "amarillos y rosas brillantes, luz cálida, ambiente alegre, campos, flores, cielos claros",
        "optimism": "verdes y dorados suaves, luz de amanecer, amanecer, caminos, montañas",
        "sadness": "azules y grises apagados, luz difusa, lluvia o neblina"
    }

    dominante = max(distribucion, key=distribucion.get)

    prompt_base = f"""
        Generá una imagen de un paisaje que represente el estado interno de una persona con las siguientes emociones:
        {', '.join([f'{k}: {v:.2f}' for k, v in distribucion.items()])}.
        La emoción dominante es {dominante}, y debe ser el foco principal de la escena.

        Estilos visuales sugeridos para cada emoción:
        - Ira → {emotion_colors['anger']}
        - Alegría → {emotion_colors['joy']}
        - Optimismo → {emotion_colors['optimism']}
        - Tristeza → {emotion_colors['sadness']}

        La imagen debe transmitir una atmósfera introspectiva, como si el paisaje fuera una metáfora del mundo interior de la persona, pero sin incluir personas ni figuras humanas. Usá elementos naturales, luz, color y composición para reflejar la intensidad emocional. Las emociones secundarias deben aparecer sutilmente en el fondo, como ecos o rastros que acompañan sin distraer.
        """
    prompt_interpretacion = f"""
        Esta imagen representa el estado emocional interno de una persona profundamente impactada por una pieza musical. Las emociones son:{distribucion}, siendo la {dominante} la dominante.
                 Usando estos estilos visuales como referencia: 
                        - Tristeza: azules y grises apagados, luz difusa, lluvia o neblina.
                        - Ira: rojos intensos, sombras oscuras, fuego, tormenta.
                        - Alegría: amarillos y rosas brillantes, luz cálida, campos, flores.
                        - Optimismo: verdes y dorados suaves, luz de amanecer, caminos, montaña.
        Describí brevemente el paisaje como un reflejo del estado emocional de esta persona. Usá un solo párrafo para transmitir las sensaciones principales que genera la escena, mostrando cómo se percibe la {dominante} en el ambiente y qué emociones secundarias se notan en el fondo. Evitá metáforas o frases poéticas: priorizá una descripción natural, clara y cercana, como si estuvieras contando lo que ves y sentís.
        """

    return prompt_base.strip(), prompt_interpretacion.strip()


# 2 Generar imagen
def generar_imagen(prompt: str) -> str:

    # Ruta del modelo
    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    response = requests.post(url, headers=HEADERS, json={"inputs": prompt})

    if response.status_code == 200:
        # Crear carpeta si no existe
        image_folder = "image"
        os.makedirs(image_folder, exist_ok=True)

        # Construir ruta completa
        image_filename = "imagen_emocional.jpg"
        image_path = os.path.join(image_folder, image_filename)

        # Guardar imagen
        image = Image.open(BytesIO(response.content))
        image.save(image_path, format="JPEG")
        print(f"✅ Imagen generada: {image_path}")
        return image_path
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        raise Exception("Error al generar imagen.")

    

# 3 SUBIR IMAGEN A IMGBB PARA OBTENER LA URL PUBLICA 

def subir_imagen_a_imgbb(ruta_imagen):
    with open(ruta_imagen, "rb") as f:
        encoded_image = base64.b64encode(f.read())
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_TOKEN,
        "image": encoded_image
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["data"]["url"]

# 4 ENVIAR PROMPT + IMAGEN A google/gemma-3-27b-it 

def generar_descripcion_emocional(prompt: str, url_publica: str, client) -> str:
    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url_publica
                        }
                    }
                ]
            }
        ],
    )
    return completion.choices[0].message.content

# 5 Calcular las emociones combinadas

def calcular_emociones_combinadas(features, lyrics_inference):
    # Normalizar audio features
    energy = features['Energy'] / 100
    danceability = features['Danceability'] / 100
    valence = features['Valence'] / 100
    acousticness = features['Acousticness'] / 100
    loudness = features['Loudness']
    loudness_factor = max(0.0, min(1.0, (loudness + 60) / 60))  # de -60 a 0 dB

    # Emociones desde audio
    emotions_from_audio = {
        "anger": (energy * 0.6) + (loudness_factor * 0.4),
        "joy": (valence * 0.7) + (danceability * 0.3),
        "optimism": (valence * 0.5) + (energy * 0.5),
        "sadness": ((1 - valence) * 0.8) + (acousticness * 0.2)
    }

    # Fusión audio + letra
    final_emotion = {}
    for key in ['anger', 'joy', 'optimism', 'sadness']:
        final_emotion[key] = round((emotions_from_audio[key] * 0.4) + (lyrics_inference[key] * 0.6), 4)

    return final_emotion


# 5 Flujo completo 

if __name__ == "__main__":

# Analisis Datos
    from app.core import DataFetcher
    from app.core.data_analyzer import DataAnalyzer

    data_fetcher = DataFetcher()
    data_analyzer = DataAnalyzer()

    user_token = "BQA9yXaB_jDrPicu4LEvZwOqugmxtCB_Hwq08gXOZYhyWpp4AzmusS_nAJXzKLpe45Yw54dUgJZ1ou8YOC38axs64PiAgPxV7udSu1Nuv7YJ0_pP67SyCVzptBsFW4R7jshxTRk4aXRxXoBh_5GNfub_JavszFGQs_VyOe8Fe0FGyRHtJSG-ZF9WxQpPokwRanIEKi2PBYqjfXdqNP4UWT9X8XpdDUjmCnrQAyms5c7tiS93BVy9d6mf"
    tracks = data_fetcher.fetch_recent_tracks(access_token=user_token)
    tracks_audio_features = data_fetcher.fetch_audio_features(tracks)
    tracks_lyrics = data_fetcher.fetch_lyrics(tracks)

    
    avg_audio = data_analyzer.average_audio_features(tracks_audio_features)
    avg_lyrics = data_analyzer.analyze_lyrics(tracks_lyrics)
    print("✅ Se obtuvieron las caracteristicas de las canciones.")

# Calcular emociones

    emotion_distribution = calcular_emociones_combinadas(avg_audio["average_audio_features"], avg_lyrics["average_lyrics_inference"])
    print("Distribución emocional:\n", emotion_distribution)
    
# Genera el promp para la imagen

    prompt_base, prompt_interpretacion = generar_prompt_emocional(emotion_distribution)
    print("🎨 Prompt generado para imagen:\n", prompt_base)


# Genera la imágen y la describe

    try:
        image_path = generar_imagen(prompt_base)
        print("✅ Imagen guardada como: ", image_path)

        print("📤 Subiendo imagen a imgbb...")
        url_publica = subir_imagen_a_imgbb(image_path)
        print("✅ Imagen subida:", url_publica)

        print("🧠 Enviando prompt e imágen al modelo...")
        descripcion = generar_descripcion_emocional(prompt_interpretacion, url_publica, client)
        print(descripcion)
    except Exception as e:
      print("❌ Error:", e)


