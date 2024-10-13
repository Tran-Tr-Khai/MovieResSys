import pandas as pd
import pickle
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data()
def data_prep():
    hybrid_df = pd.read_csv('D:/Project/movie-rec-system/hybrid_df (1).csv', delimiter=',', quotechar='"')
    tfidf_matrix = pickle.load(open('D:/Project/movie-rec-system/tfidf_matrix.pkl', 'rb'))

    cos_sim = cosine_similarity(tfidf_matrix)

    return hybrid_df, cos_sim

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
    return final_df_sorted['title'].reset_index(drop=True).iloc[1:]

def main(): 
    html_temp = '''
    <h1 style="font-family: Trebuchet MS; padding: 12px; font-size: 30px; color: #780116; text-align: center;
    line-height: 1.25;">Recommender System<br>
    <span style="color: #f7b538; font-size: 48px"><b>Movie Recommendation</b></span><br>
    </h1>
    <hr>
    '''
    st.markdown(html_temp, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown('<h1 style="font-family: Trebuchet MS; padding: 12px; font-size: 22px; color: #c32f27; text-align: left; line-height: 1.25;"><u>Input</u></h1>', unsafe_allow_html=True)

        movie = st.text_input('Movie Title', '')
        top_n = st.slider('Top n Result', 1, 10, 10)

        if st.button('Find', key='1'):
            title = movie
            top = top_n
        
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

    with col3:
        st.markdown('<h1 style="font-family: Trebuchet MS; padding: 12px; font-size: 22px; color: #c32f27; text-align: left; line-height: 1.25;"><u>Result</u></h1>', unsafe_allow_html=True)

        try:
            # Chỉ gọi predict nếu title có giá trị
            if 'title' in locals():
                result = predict(title, similarity_weight=0.7, top_n=top)
                if not result.empty:
                    st.dataframe(result)
                else:
                    st.write("No results found for the movie title entered.")
            else:
                st.write("Please enter a movie title.")
        except Exception as e:
            st.write(f"An error occurred: {e}")

if __name__ == '__main__':
    main()