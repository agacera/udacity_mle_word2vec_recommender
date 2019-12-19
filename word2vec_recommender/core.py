#AUTOGENERATED! DO NOT EDIT! File to edit: dev/00_core.ipynb (unless otherwise specified).

__all__ = ['RANDOM_SEED', 'logger', 'Recommendation', 'Movie', 'MovieRepository', 'print_recommendations']

#Cell
from typing import List, NamedTuple, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

import pandas as pd
import matplotlib.pyplot as plt

#Cell
# constants
RANDOM_SEED = 31

logger = logging.getLogger(__name__)

#Cell
class Recommendation(NamedTuple):
    """
    Represents a recommendation for a movie
    """
    movie_id: int
    score: float

#Cell
@dataclass
class Movie:
    """
    Simple dataclass to hold the content for a Movie
    """
    movie_id: int
    title: str
    genres: str

#Cell
class MovieRepository:
    def __init__(
        self,
        movies_df: pd.DataFrame):
        self.movies_df = movies_df
        self.movie_id_dict = movies_df.set_index("movieId").to_dict('index')

    def find_by_movie_id(self, movie_id: int) -> Movie:
        movie_row = self.movie_id_dict[movie_id]
        return Movie(
            movie_id=movie_id,
            title=movie_row['title'],
            genres=movie_row['genres']
        )


#Cell
def print_recommendations(movie_repository: MovieRepository, seed_id: int, recommendations: List[Recommendation]):
    seed = movie_repository.find_by_movie_id(seed_id)
    print(seed)
    print("> Recommendations:")
    for rec in recommendations:
        movie = movie_repository.find_by_movie_id(rec.movie_id)
        print(">>", movie, f"score={rec.score}")