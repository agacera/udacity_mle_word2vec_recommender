#AUTOGENERATED! DO NOT EDIT! File to edit: dev/03_tmdb.ipynb (unless otherwise specified).

__all__ = ['load_api_key', 'MovieData', 'TmdbApi']

#Cell
from dataclasses import dataclass
from functools import lru_cache

import requests

import pandas as pd

#Cell
def load_api_key():
    import os
    key = os.environ.get('TMDB_API_KEY')
    if key:
        return key
    raise RuntimeError("TMDB_API_KEY is not defined")

#Cell
@dataclass
class MovieData:
    movie_id: int
    tmdb_id: int
    title: str
    image_url: str

#Cell
class TmdbApi:
    def __init__(self, api_key: str, movielens_to_tmdb_lookup: dict):
        self.api_key = api_key
        self.movielens_to_tmdb_lookup = {int(movielens_id):int(tmdb_id) for movielens_id, tmdb_id in movielens_to_tmdb_lookup.items() }
        self.tmdb_to_movielens_lookup = {int(tmdb_id):int(movielens_id) for movielens_id, tmdb_id in movielens_to_tmdb_lookup.items() }

    @lru_cache(maxsize=100_000)
    def fetch_movie_data_by_tmdb_id(self, tmdb_movie_id: int) -> MovieData:
        print(">tmdb_movie_id", tmdb_movie_id)
        data = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_movie_id}?api_key={self.api_key}").json()
        poster_path = data.get("poster_path")
        return MovieData(
            movie_id=self.tmdb_to_movielens_lookup.get(tmdb_movie_id),
            tmdb_id=tmdb_movie_id,
            title=data.get('title'),
            image_url=f'https://image.tmdb.org/t/p/w185{poster_path}'
        )

    def fetch_movie_data_by_movielens_id(self, movielens_id: int) -> MovieData:
        tmdb_id = self.movielens_to_tmdb_lookup.get(movielens_id)
        return self.fetch_movie_data_by_tmdb_id(tmdb_id)
