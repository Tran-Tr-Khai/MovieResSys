import requests
from dotenv import load_dotenv
import mysql.connector
import os 
import json
import time


def init_mysql_movies(mysql_conn, res):
    cursor = mysql_conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS movies (
            genre_ids JSON, 
            id INT PRIMARY KEY,
            original_language VARCHAR(10),
            overview TEXT,
            popularity DOUBLE,
            release_date TEXT,
            title VARCHAR(255),
            vote_average DOUBLE,
            vote_count INT
        );
        """
    )

    insert_query = """
    INSERT INTO movies (genre_ids, id, original_language, overview, popularity, release_date, title, vote_average, vote_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    original_language = VALUES(original_language),
    overview = VALUES(overview),
    popularity = VALUES(popularity),
    release_date = VALUES(release_date),
    title = VALUES(title),
    vote_average = VALUES(vote_average),
    vote_count = VALUES(vote_count);
    """

    for movie in res["results"]:
        genre_ids_str = json.dumps(movie["genre_ids"])
        cursor.execute(insert_query, (
            genre_ids_str, movie['id'], movie['original_language'],
            movie['overview'], movie['popularity'], movie['release_date'] + ' 00:00:00',
            movie['title'], movie['vote_average'], movie['vote_count']
        ))

    mysql_conn.commit()
    cursor.close()


def init_mysql_genres(mysql_conn, genres_data):
    cursor = mysql_conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS genres (
            id INT PRIMARY KEY,
            name VARCHAR(100)
        );
        """
    )

    insert_query = """
    INSERT INTO genres (id, name)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
    name = VALUES(name);
    """

    for genre in genres_data:
        cursor.execute(insert_query, (genre['id'], genre['name']))

    mysql_conn.commit()
    cursor.close()


def drop_existing_tables(mysql_conn):
    cursor = mysql_conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS movies;")
    cursor.execute("DROP TABLE IF EXISTS genres;")
    print("Dropped existing tables.")
    cursor.close()

def get_movies(lang, freq, mysql_conn, api_key):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&with_original_language={lang}"
    movies = 0
    page = 1
    progress = 0

    drop_existing_tables(mysql_conn)

    while movies < freq:
        try:
            res = requests.get(url + "&page=" + str(page))
            
            # Nếu nhận mã lỗi 429, tạm dừng 5 giây rồi thử lại
            if res.status_code == 429:
                print("Too many requests. Waiting for 5 seconds...")
                time.sleep(5)
                continue

            res.raise_for_status()  # Raise error nếu có mã lỗi khác ngoài 429
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")
            break

        res_json = res.json()

        if "errors" in res_json.keys():
            print("API error!")
            return movies

        movies += len(res_json["results"])
        init_mysql_movies(mysql_conn, res_json)

        new_progress = round(movies / freq * 100)
        if new_progress != progress:
            progress = new_progress
            if progress % 5 == 0:
                print(progress, end="%, ")

        page += 1
        time.sleep(0.1)  # Thêm khoảng cách giữa các yêu cầu để tránh vượt quá giới hạn API

    return movies


def get_genres(lang, mysql_conn, api_key):
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&with_original_language={lang}"

    try:
        res = requests.get(url)
        
        # Nếu gặp lỗi 429 thì tạm dừng 5 giây rồi thử lại
        if res.status_code == 429:
            print("Too many requests. Waiting for 5 seconds...")
            time.sleep(5)
            return get_genres(lang, mysql_conn, api_key)  # Thử lại yêu cầu

        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []

    res_json = res.json()

    if "errors" in res_json.keys():
        print("API error!")
        return []

    genres_data = res_json["genres"]
    init_mysql_genres(mysql_conn, genres_data)

    return len(genres_data)


if __name__ == "__main__":
    load_dotenv("D:\Project\movie-rec-system\.env")
    api_key = os.getenv("API_KEY")
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    mysql_conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    try:
        language_count = {
            "en": 10000,  # Số lượng phim mà bạn muốn tải về
        }

        for lang, freq in language_count.items():
            print(f"Downloading {lang}: ", end="")
            movies = get_movies(lang, freq, mysql_conn, api_key)
            print(f"Total movies found: {movies}")
            genres = get_genres(lang, mysql_conn, api_key)
            print(f"Total genres found: {genres}")

    finally:
        mysql_conn.close()