import streamlit as st
import pickle
import pandas as pd
import requests
import time

# Must be first command
st.set_page_config(page_title="🎬 Cine-Buddy", layout="wide")

# Constants
API_KEY = "7acdc7bf1d7d81d4bdddd7be7610da0d"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Dynamic Styling for Light Mode
st.markdown("""
    <style>
    body {
        background-color: #1c1c1c;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .movie-card {
        background-color: #2e2e2e;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: 0.3s ease-in-out;
        text-align: center;
        height: 550px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        color: white;
    }
    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
        background-color: #444444;
    }
    .movie-title {
        color: #ffb14e;
        font-weight: bold;
        margin: 10px 0;
        font-size: 1.5rem;
        height: 45px;
        overflow: hidden;
    }
    .movie-rating {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffd700;
        margin-top: 10px;
    }
    .movie-desc {
        font-size: 1rem;
        color: #bbb;
        margin-top: auto;
        max-height: 120px;
        overflow-y: auto;
        text-align: left;
        padding: 0.5rem;
        background-color: rgba(255,255,255,0.1);
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .movie-card img {
        max-height: 250px;
        border-radius: 10px;
        object-fit: cover;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
    }
    .movie-container {
        display: flex;
        flex-wrap: wrap;
        gap: 25px;
        justify-content: center;
    }
    .stButton button {
        background-color: #ffb14e;
        color: #333;
        border-radius: 5px;
        font-weight: bold;
        padding: 12px 30px;
        transition: 0.3s ease;
    }
    .stButton button:hover {
        background-color: #f8b400;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)


# API Helpers
def fetch_details(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return {
            'poster': f"https://image.tmdb.org/t/p/w500/{data['poster_path']}" if data.get(
                'poster_path') else "https://via.placeholder.com/500x750.png?text=No+Image",
            'desc': data.get('overview', 'No description available.'),
            'rating': data.get('vote_average', 'N/A'),
            'genres': [genre['name'] for genre in data.get('genres', [])]
        }
    except:
        return {
            'poster': "https://via.placeholder.com/500x750.png?text=No+Image",
            'desc': 'No description available.',
            'rating': 'N/A',
            'genres': []
        }


def recommend(movie, selected_genre):
    if movie == "None":
        return []  # Return an empty list if "None" is selected

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:10]

    recommended = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        movie_title = movies.iloc[i[0]].title
        details = fetch_details(movie_id)

        if selected_genre and selected_genre != "None" and selected_genre not in details['genres']:
            continue

        recommended.append({
            'title': movie_title,
            'poster': details['poster'],
            'desc': details['desc'],
            'rating': details['rating']
        })

        if len(recommended) >= 5:
            break

        time.sleep(0.4)  # avoid TMDB rate limits

    return recommended


# Load Data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Title
st.title("🎬 Cine-Buddy - Movie Recommender")
st.markdown("### Discover your next favorite movie!")

# Genre Filter
genre_options = ["None", "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
                 "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance",
                 "Science Fiction", "TV Movie", "Thriller", "War", "Western"]
selected_genre = st.selectbox("🎭 Filter by Genre (optional)", genre_options)

# Movie Selection with "None" Option
selected_movie_name = st.selectbox('🎥 Search Movie', ["None"] + list(movies['title'].values))

# Recommend Button
if st.button('🍿 Recommend Movies'):
    results = recommend(selected_movie_name, selected_genre)

    if not results:
        st.warning("No recommendations found for the selected genre or movie.")
    else:
        st.markdown("### Recommended Movies")
        movie_container = st.container()
        with movie_container:
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                if idx < len(results):
                    movie = results[idx]
                    with col:
                        rating = movie['rating']
                        # Updated rating display **with a star symbol ⭐**
                        if rating != 'N/A':
                            rating_display = f'<span style="font-size: 1.5rem; font-weight: bold; color: #ffd700;">⭐ {float(rating):.1f}/10</span>'
                        else:
                            rating_display = '<span style="font-size: 1.3rem; color: #bbb;">No rating available</span>'

                        st.markdown(f"""
                            <div class="movie-card">
                                <img src="{movie['poster']}" />
                                <div class="movie-title">{movie['title']}</div>
                                <div class="movie-rating">{rating_display}</div>
                                <div class="movie-desc">{movie['desc']}</div>
                            </div>
                        """, unsafe_allow_html=True)