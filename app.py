import pandas as pd
import streamlit as st
import pickle
import requests

# ================= Fetch Poster + Extra Info ================= #
def fetch_movie_details(movie_id, use_api=True):
    if not use_api:
        return (
            "https://via.placeholder.com/150",
            "Unknown Title",
            "N/A",
            "Overview not available."
        )

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=212fdebc2c7095a2e4c3caa4780d903f&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        poster = "https://image.tmdb.org/t/p/w500" + str(data.get('poster_path', ""))
        title = data.get("title", "Unknown Title")
        rating = data.get("vote_average", "N/A")
        overview = data.get("overview", "No description available.")
        return poster, title, rating, overview

    except requests.exceptions.Timeout:
        return "https://via.placeholder.com/150", "Timeout Error", "N/A", "Could not fetch details (timeout)."
    except requests.exceptions.RequestException as e:
        return "https://via.placeholder.com/150", "API Error", "N/A", str(e)

# ================= Recommendation Function ================= #
def recommend(movie1, use_api=True):
    movie_index = movie[movie['title'] == movie1].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        movie_id = movie.iloc[i[0]].movie_id
        poster, title, rating, overview = fetch_movie_details(movie_id, use_api)
        if title in ["Unknown Title", "Timeout Error", "API Error"]:
            title = movie.iloc[i[0]].title
        recommended_movies.append({
            "title": title,
            "poster": poster,
            "rating": rating,
            "overview": overview
        })
    return recommended_movies

# ================= Load Data ================= #
movie_dict = pickle.load(open('movies_dict.pkl','rb'))
movie = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl','rb'))   # <-- Local file

# ================= Streamlit UI ================= #
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: white;
        font-family: 'Arial';
    }
    h1 {
        text-align: center;
        color: #facc15;
    }
    .movie-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
        min-height: 350px;
    }
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
        color: #facc15;
    }
    .movie-rating {
        font-size: 14px;
        color: #38bdf8;
    }
    .movie-overview {
        font-size: 12px;
        color: #e2e8f0;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Settings")
use_api = st.sidebar.checkbox("Use TMDB API (posters, ratings, overview)", value=True)
st.sidebar.markdown("---")
st.sidebar.info("Made by **Shubhankar Khatik**\n\n📍 Institute of Engineering and Technology, Lucknow")

# Title
st.title("🎬 Movie Recommender System")

# Search box
selected_movie_name = st.selectbox(
    "Search for a movie:",
    movie['title'].values
)

# Recommendation section
if st.button('Show Recommendations'):
    recommendations = recommend(selected_movie_name, use_api)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        if idx < len(recommendations):
            with col:
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{recommendations[idx]['poster']}" width="150">
                    <div class="movie-title">{recommendations[idx]['title']}</div>
                    <div class="movie-rating">⭐ {recommendations[idx]['rating']}</div>
                    <div class="movie-overview">{recommendations[idx]['overview'][:100]}...</div>
                </div>
                """, unsafe_allow_html=True)
