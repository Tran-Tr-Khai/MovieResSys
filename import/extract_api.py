import requests
import time

class extract:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_data(self, endpoint, params=None, retries=3):
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key

        for attempt in range(retries):
            try:
                res = requests.get(url, params=params)

                if res.status_code == 429:  # Quá nhiều request
                    print("Too many requests. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                res.raise_for_status()
                return res.json()
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    raise

    def get_popular_movies(self, lang, page):
        return self.fetch_data("movie/popular", {"with_original_language": lang, "page": page})

    def get_genres(self, lang):
        return self.fetch_data("genre/movie/list", {"with_original_language": lang})