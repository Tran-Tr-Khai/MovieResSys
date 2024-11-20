from dotenv import load_dotenv
import os 
import requests
import pandas as pd
import pickle
import json
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import base64

load_dotenv(".env")
API_KEY = os.getenv("API_KEY")
BASE_URL = 'https://api.themoviedb.org/3/'

@st.cache_data()
def data_prep():
    hybrid_df = pd.read_csv('C:\\Users\\trong\\OneDrive\\Documents\\Project\\MovieResSys\\EDA\\hybrid_df.csv', delimiter=',', quotechar='"')
    tfidf_matrix = pickle.load(open('C:\\Users\\trong\\OneDrive\\Documents\\Project\\MovieResSys\\tfidf_matrix.pkl', 'rb'))

    cos_sim = cosine_similarity(tfidf_matrix)

    return hybrid_df, cos_sim

# Hàm lấy ảnh từ TMDb API theo tên phim
def get_movie_image(movie_name):
    search_url = f"{BASE_URL}search/movie?api_key={API_KEY}&query={movie_name}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            # Lấy ID của phim đầu tiên trong kết quả
            movie_id = data['results'][0]['id']
            
            # Lấy ảnh của phim từ ID
            image_url = f"{BASE_URL}movie/{movie_id}/images?api_key={API_KEY}"
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                image_data = image_response.json()
                if 'posters' in image_data and image_data['posters']:
                    # Lấy đường dẫn ảnh đầu tiên
                    poster_path = image_data['posters'][0]['file_path']
                    full_image_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                    return full_image_url
    return None

def predict(title, similarity_weight=0.7, top_n=10):
    hybrid_df, cos_sim = data_prep()
    
    data = hybrid_df.reset_index()
    index_movie = data[data['title'] == title].index

    # Kiểm tra xem có chỉ số nào không
    if index_movie.empty:
        return pd.DataFrame()  # Trả về DataFrame rỗng nếu không tìm thấy phim

    similarity = cos_sim[index_movie].T
    sim_df = pd.DataFrame(similarity, columns=['similarity'])
    final_df = pd.concat([data, sim_df], axis=1)
    final_df['final_score'] = final_df['score'] * (1 - similarity_weight) + final_df['similarity'] * similarity_weight
    
    final_df_sorted = final_df.sort_values(by='final_score', ascending=False).iloc[:top_n + 1]
    
    # Thêm ảnh vào kết quả gợi ý
    final_df_sorted['image_url'] = final_df_sorted['title'].apply(get_movie_image)
    
    return final_df_sorted[['title', 'image_url']]

def display_header():
    html_temp = '''
    <h1 style="font-family: Trebuchet MS; padding: 12px; font-size: 30px; color: #780116; text-align: center;
    line-height: 1.25;">Recommender System<br>
    <span style="color: #f7b538; font-size: 48px"><b>Movie Recommendation</b></span><br>
    </h1>
    <hr>
    '''
    st.markdown(html_temp, unsafe_allow_html=True)


def get_user_input():
    st.markdown('<h1 style="font-family: Trebuchet MS; padding: 12px; font-size: 22px; color: #c32f27; text-align: left; line-height: 1.25;"><u>Input</u></h1>', unsafe_allow_html=True)
    movie = st.text_input('Movie Title', '')
    top_n = st.slider('Top n Result', 1, 10, 10)
    return movie, top_n


def display_results(title, top_n):
    st.markdown('<h1 style="font-family: Trebuchet MS; padding: 12px; font-size: 22px; color: #c32f27; text-align: left; line-height: 1.25;"><u>Result</u></h1>', unsafe_allow_html=True)

    try:
        if title:
            result = predict(title, similarity_weight=0.7, top_n=top_n)
            if not result.empty:
                for _, row in result.iterrows():
                    st.write(f"**{row['title']}**")
                    if row['image_url']:
                        st.image(row['image_url'], caption=row['title'], use_column_width=True)
            else:
                st.write("No results found for the movie title entered.")
        else:
            st.write("Please enter a movie title.")
    except Exception as e:
        st.write(f"An error occurred: {e}")
        
def display_help():
    with st.expander('No output?'):
        st.write('''If there's no output in the result section, make sure you have typed the right movie title.
        
        You can try these 6 movies:
        1. Toy Story
        2. Iron Man
        3. The Conjuring
        4. Home Alone
        5. The Lord of the Rings
        6. Titanic
        ''')

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background_local(image_path):
    bin_str = get_base64_of_bin_file(image_path)
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

def main():
    set_background_local("C:\\Users\\trong\\OneDrive\\Documents\\Project\\MovieResSys\\background.jpg") 
    display_header()
    col1, col3 = st.columns([2, 2])

    with col1:
        movie, top_n = get_user_input()
        if st.button('Find', key='1'):
            display_help()


    with col3:
        if movie:
            display_results(movie, top_n)


if __name__ == '__main__':
    main()

