import os
from dotenv import load_dotenv
from connect_mysql import MySQLConnector
from extract_api import extract

def initialize_tables(db_handler):
    db_handler.create_table("""
        CREATE TABLE IF NOT EXISTS movies (
            genre_ids JSON,
            id INT PRIMARY KEY,
            original_language VARCHAR(10),
            overview TEXT,
            popularity DOUBLE,
            release_date DATETIME,
            title VARCHAR(255),
            vote_average DOUBLE,
            vote_count INT
        );
    """)

    db_handler.create_table("""
        CREATE TABLE IF NOT EXISTS genres (
            id INT PRIMARY KEY,
            name VARCHAR(100)
        );
    """)

def fetch_and_store_movies(lang, freq, db_handler, tmdb_handler):
    db_handler.drop_table("movies")
    initialize_tables(db_handler)

    total_movies = 0
    page = 1

    while total_movies < freq:
        movies_data = tmdb_handler.get_popular_movies(lang, page)
        results = movies_data.get("results", [])

        if not results:
            break

        formatted_movies = db_handler.format_movies_data(results)
        db_handler.insert_data("""
            INSERT INTO movies (genre_ids, id, original_language, overview, popularity, release_date, title, vote_average, vote_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            original_language=VALUES(original_language),
            overview=VALUES(overview),
            popularity=VALUES(popularity),
            release_date=VALUES(release_date),
            title=VALUES(title),
            vote_average=VALUES(vote_average),
            vote_count=VALUES(vote_count);
        """, formatted_movies)

        total_movies += len(results)
        print(f"Downloaded {total_movies}/{freq} movies...")
        page += 1

    return total_movies

def fetch_and_store_genres(lang, db_handler, tmdb_handler):
    db_handler.drop_table("genres")
    initialize_tables(db_handler)

    genres_data = tmdb_handler.get_genres(lang).get("genres", [])
    formatted_genres = db_handler.format_genres_data(genres_data)

    db_handler.insert_data("""
        INSERT INTO genres (id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name=VALUES(name);
    """, formatted_genres)

    return len(formatted_genres)

if __name__ == "__main__":
    load_dotenv(".env")

    api_key = os.getenv("API_KEY")
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    tmdb_handler = extract(api_key)
    db_handler = MySQLConnector(**db_config)

    try:
        lang = "en"
        movie_count = fetch_and_store_movies(lang, 10000, db_handler, tmdb_handler)
        print(f"Total movies stored: {movie_count}")

        genre_count = fetch_and_store_genres(lang, db_handler, tmdb_handler)
        print(f"Total genres stored: {genre_count}")

    finally:
        db_handler.close()