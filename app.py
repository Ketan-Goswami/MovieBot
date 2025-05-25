import streamlit as st
import pickle 
import requests



import time
from requests.exceptions import ConnectionError, Timeout, RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed

poster_cache = {}

def fetch_poster(movie_id):
    if movie_id in poster_cache:
        return poster_cache[movie_id]

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9590cc4df712427fa98b2e17377b8240&language=en-US"
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                full_path = "https://via.placeholder.com/500x750?text=No+Image"
            poster_cache[movie_id] = full_path
            return full_path
        except (ConnectionError, Timeout) as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # reduced wait before retrying
                continue
            else:
                full_path = "https://via.placeholder.com/500x750?text=No+Image"
                poster_cache[movie_id] = full_path
                return full_path
        except RequestException as e:
            full_path = "https://via.placeholder.com/500x750?text=No+Image"
            poster_cache[movie_id] = full_path
            return full_path

def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_sorted = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_movie_id = {executor.submit(fetch_poster, movies_df.iloc[i[0]].movie_id): i for i in movies_sorted}
        for future in as_completed(future_to_movie_id):
            i = future_to_movie_id[future]
            movie_id = movies_df.iloc[i[0]].movie_id
            recommended_movie_names.append(movies_df.iloc[i[0]].title)
            try:
                poster_url = future.result()
            except Exception:
                poster_url = "https://via.placeholder.com/500x750?text=No+Image"
            recommended_movie_posters.append(poster_url)

    # Sort results to maintain order as per movies_sorted
    combined = list(zip(recommended_movie_names, recommended_movie_posters))
    combined_sorted = sorted(combined, key=lambda x: movies_list.tolist().index(x[0]))
    recommended_movie_names, recommended_movie_posters = zip(*combined_sorted)

    return list(recommended_movie_names), list(recommended_movie_posters)

# Load the movies and similarity data
movies_df = pickle.load(open('movies.pkl', 'rb'))
movies_list = movies_df['title'].values

similarity = pickle.load(open('similarity.pkl', 'rb'))


st.title("Movie Recommendation System")
selected_movie_name = st.selectbox(
"Type or select a movie from the dropdown",
movies_list)

# Display the recommendation button and output
if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie_name)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
        
        
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])
       
        
    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
       
    
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
       
    
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])