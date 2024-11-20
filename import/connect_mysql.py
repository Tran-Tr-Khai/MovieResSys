import mysql.connector
import json

class MySQLConnector:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.connection.cursor()

    def create_table(self, table_query):
        self.cursor.execute(table_query)

    def insert_data(self, query, data):
        self.cursor.executemany(query, data)
        self.connection.commit()

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

    def close(self):
        self.cursor.close()
        self.connection.close()

    @staticmethod
    def format_movies_data(results):
        return [
            (
                json.dumps(movie["genre_ids"]), movie["id"], movie["original_language"],
                movie["overview"], movie["popularity"],
                movie['release_date'] if movie['release_date'] and movie['release_date'].strip() != '00:00:00' else None,
                movie["title"],
                movie["vote_average"], movie["vote_count"]
            )
            for movie in results
        ]
    @staticmethod
    def format_genres_data(genres):
        return [(genre["id"], genre["name"]) for genre in genres]