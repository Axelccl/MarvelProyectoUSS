import streamlit as st
import requests
import hashlib
import time
import urllib3
import ssl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random

public_key = '1ed6c793519f923d12e3f7204e229421'
private_key = '4f7ca42647a5368f658e001203e7b5cf1f03db2a'
base_url = "https://gateway.marvel.com/v1/public/"

google_ai_api_key = 'AIzaSyD0gKxScfhaXo-fVyDtJrJLYs_GDSD9tl8'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def create_session():
    session = requests.Session()
    session.mount('https://', TLSAdapter())
    return session

def get_random_comics(exclude_ids):
    timestamp = str(int(time.time()))
    hash_value = hashlib.md5((timestamp + private_key + public_key).encode("utf-8")).hexdigest()
    url = f"{base_url}comics?ts={timestamp}&apikey={public_key}&hash={hash_value}&limit=100"

    try:
        session = create_session()
        response = session.get(url)
        if response.status_code == 200:
            data = response.json()
            comics = data['data']['results']
            new_comics = [comic for comic in comics if comic['id'] not in exclude_ids]
            return random.sample(new_comics, min(25, len(new_comics)))
        else:
            st.error(f"Error al obtener cómics aleatorios: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error al obtener cómics aleatorios: {str(e)}")

    return []

def get_marvel_characters_with_requests(search_term):
    if search_term:
        timestamp = str(int(time.time()))
        hash_value = hashlib.md5((timestamp + private_key + public_key).encode("utf-8")).hexdigest()
        url = f"{base_url}characters?nameStartsWith={search_term}&ts={timestamp}&apikey={public_key}&hash={hash_value}"
        try:
            session = create_session()
            response = session.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['data']['results']
            else:
                st.error(f"Error al obtener datos de la API de Marvel: {response.status_code} - {response.text}")
        except requests.exceptions.SSLError as e:
            st.error(f"SSL Error with requests: {str(e)}")
        except Exception as e:
            st.error(f"Error with requests: {str(e)}")
    return []

def get_character_comics(character_id):
    timestamp = str(int(time.time()))
    hash_value = hashlib.md5((timestamp + private_key + public_key).encode("utf-8")).hexdigest()
    url = f"{base_url}characters/{character_id}/comics?ts={timestamp}&apikey={public_key}&hash={hash_value}"

    try:
        session = create_session()
        response = session.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['data']['results']
        else:
            st.error(f"Error al obtener cómics del personaje: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error al obtener cómics: {str(e)}")
    return []

def show_character_comics(character_name, comics):
    if comics:
        st.subheader(f"Cómics de {character_name}:")
        for comic in comics:
            title = comic['title']
            description = comic.get('description', 'Sin descripción')
            thumbnail_path = comic['thumbnail']['path']
            thumbnail_extension = comic['thumbnail']['extension']
            image_url = f"{thumbnail_path}.{thumbnail_extension}"
            comic_url = comic['urls'][0]['url'] if comic['urls'] else '#'

            if thumbnail_extension:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(image_url, use_container_width='200', caption=title)
                with col2:
                    st.markdown(f"**Descripción:** {description if description else 'Sin descripción'}")
                    st.markdown(f"**Enlace:** [{comic_url}] ({comic_url})")
            else:
                st.warning(f"El cómic '{title}' no tiene portada disponible.")
    else:
        st.write(f"No se encontraron cómics para {character_name}.")

def handle_graph_questions(question, characters):
    if "poder" in question.lower():
        power_data = {character['name']: np.random.randint(70, 100) for character in characters}
        names = list(power_data.keys())
        values = list(power_data.values())

        plt.figure(figsize=(10, 6))
        sns.barplot(x=names, y=values, palette='viridis')
        plt.title("Escala de Poderes de Personajes de Marvel", fontsize=16)
        plt.xlabel("Personajes", fontsize=12)
        plt.ylabel("Poder", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif "buscados" in question.lower():
        search_data = {character['name']: np.random.randint(100, 600) for character in characters}
        names = list(search_data.keys())
        values = list(search_data.values())

        plt.figure(figsize=(10, 6))
        sns.barplot(x=names, y=values, palette='coolwarm')
        plt.title("Personajes Más Buscados de Marvel", fontsize=16)
        plt.xlabel("Personajes", fontsize=12)
        plt.ylabel("Búsquedas", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(plt)

def get_character_trivia(character_name):
    trivia = {
        "Spider-Man": "Spider-Man fue creado por Stan Lee y Steve Ditko y apareció por primera vez en Amazing Fantasy #15 en 1962.",
        "Iron Man": "Tony Stark, también conocido como Iron Man, es un genio inventor y multimillonario.",
        "Hulk": "Bruce Banner se convierte en Hulk cuando se expone a radiación gamma.",
        "Thor": "Thor es el Dios del Trueno y proviene de Asgard.",
        "Captain America": "Steve Rogers se convirtió en Captain America después de recibir un suero experimental durante la Segunda Guerra Mundial.",
        "Capitana Marvel": "Carol Danvers se convierte en Capitana Marvel tras ser expuesta a la energía de una explosión de un dispositivo de luz.",
        "Black Widow": "Natasha Romanoff, también conocida como Black Widow, es una ex-espía de la KGB y una experta en combate.",
        "Doctor Strange": "Doctor Strange fue un neurocirujano antes de convertirse en el Hechicero Supremo."
    }
    return trivia.get(character_name, "No hay datos curiosos disponibles.")

def ask_about_character(question, character_name):
    prompt = f"Por favor, proporciona información sobre {character_name} en respuesta a la siguiente pregunta: {question}"
    headers = {
        "Content-Type": "application/json"
    }
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={google_ai_api_key}"

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        answer = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
        return answer
    else:
        st.error(f"Error al obtener respuesta de Google AI Studio: {response.status_code} - {response.text}")
    return "No se pudo obtener una respuesta."

st.markdown("""
<style>
body {
    background-image: url('https://wallpapers.com/images/hd/4k-marvel-digital-cartoon-t9z4pnuivn6488jq.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    opacity: 0.9;
}
h1, h2, h3 {
    color: #c8102e;
}
</style>
""", unsafe_allow_html=True)

st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjmHn7hDycWvYvGnj50dxygz2EUz8MBKKCqg&s", use_container_width=False, width=600)
st.header("Explora el Universo Marvel")
st.text("Bienvenido a la aplicación de Marvel. Busca personajes y haz preguntas sobre ellos.")
st.markdown("---")

banner_url = "https://cdn.marvel.com/content/2x/immortal-thor-desktop.jpg"
col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    st.image(banner_url, use_container_width=False, width=600)

col1, col2 = st.columns([1, 8])
with col1:
    if st.button("Inicio"):
        st.session_state.page = "Inicio"
with col2:
    if st.button("Cómics"):
        st.session_state.page = "Cómics"

if 'page' not in st.session_state:
    st.session_state.page = "Inicio"

if st.session_state.page == "Inicio":
    st.subheader("Bienvenido a la sección de inicio")
    st.text("Aquí puedes buscar personajes y hacer preguntas sobre ellos.")

    search_term = st.text_input("Buscar personaje:", placeholder="Introduce el nombre del personaje...")

    if 'favorites' not in st.session_state:
        st.session_state.favorites = []

    characters = get_marvel_characters_with_requests(search_term)

    selected_character_id = None

    if characters:
        st.subheader("Personajes encontrados:")
        for character in characters:
            name = character['name']
            description = character.get('description', 'Sin descripción')
            thumbnail_path = character['thumbnail']['path']
            thumbnail_extension = character['thumbnail']['extension']
            image_url = f"{thumbnail_path}.{thumbnail_extension}"

            col1, col2 = st.columns([1, 2])
            with col1:
                if thumbnail_extension:
                    st.image(image_url, use_container_width='auto', caption=name)
                else:
                    st.warning(f"El personaje '{name}' no tiene imagen disponible.")
            with col2:
                st.markdown(f"**Nombre:** {name}")
                st.markdown(f"**Descripción:** {description if description else 'Sin descripción'}")
                st.markdown("---")

                if st.button("❤️ Agregar a Favoritos", key=name):
                    if name not in st.session_state.favorites:
                        st.session_state.favorites.append(name)
                        st.success(f"{name} ha sido agregado a tus favoritos.")
                    else:
                        st.warning(f"{name} ya está en tus favoritos.")

                if st.button("❌ Eliminar de Favoritos", key=f"remove_{name}"):
                    if name in st.session_state.favorites:
                        st.session_state.favorites.remove(name)
                        st.success(f"{name} ha sido eliminado de tus favoritos.")
                    else:
                        st.warning(f"{name} no está en tus favoritos.")

                if selected_character_id is None:
                    selected_character_id = character['id']

    if st.session_state.favorites:
        st.subheader("Tus Personajes Favoritos:")
        for favorite in st.session_state.favorites:
            st.write(f"- {favorite}")

    st.header("Preguntas sobre Personajes")
    question = st.text_input("¿Qué quieres saber sobre un personaje?")
    st.markdown("Ejemplos de preguntas: '¿Cuántos cómics tiene Spider-Man?', '¿Qué poderes tiene Iron Man?'")

    if question:
        selected_character = st.selectbox("Selecciona un personaje:", [character['name'] for character in characters])
        selected_character_id = next(
            character['id'] for character in characters if character['name'] == selected_character)

        if st.button("Preguntar"):
            answer = ask_about_character(question, selected_character)
            st.write(f"**Respuesta sobre {selected_character}: {answer}")

            trivia = get_character_trivia(selected_character)
            st.write(f"**Trivia sobre {selected_character}:** {trivia}")

    st.header("Preguntas sobre Gráficos")
    graph_question = st.text_input("¿Qué gráfico te gustaría ver? (Ejemplo: 'poder', 'buscados')")

    if graph_question:
        handle_graph_questions(graph_question, characters)

elif st.session_state.page == "Cómics":
    st.subheader("Cómics")
    if 'shown_comic_ids' not in st.session_state:
        st.session_state.shown_comic_ids = []

    random_comics = get_random_comics(st.session_state.shown_comic_ids)

    if random_comics:
        num_cols = 4
        cols = st.columns(num_cols)

        for i, comic in enumerate(random_comics):
            thumbnail_path = comic['thumbnail']['path']
            thumbnail_extension = comic['thumbnail']['extension']
            image_url = f"{thumbnail_path}.{thumbnail_extension}" if thumbnail_extension else None
            comic_url = comic['urls'][0]['url'] if comic['urls'] else '#'

            if image_url:
                left_col, center_col, right_col = st.columns([1, 2, 1])

                with center_col:
                    st.image(image_url, use_container_width ='auto', caption=comic['title'])
                    st.markdown (f"[Ver más detalles]({comic_url})", unsafe_allow_html=True)

                st.session_state.shown_comic_ids.append(comic['id'])
            else:
                st.warning(f"El cómic '{comic['title']}' no tiene portada disponible.")
    else:
        st.write("No se encontraron cómics aleatorios.")

st.markdown("""
<style>
img {
    transition: transform 0.2s;
}
</style>
""", unsafe_allow_html=True)
