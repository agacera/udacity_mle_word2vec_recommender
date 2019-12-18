#AUTOGENERATED! DO NOT EDIT! File to edit: dev/00_model.ipynb (unless otherwise specified).

__all__ = ['RANDOM_SEED', 'logger', 'GensimParameters', 'generate_sentences_by_user', 'Recommendation', 'Movie',
           'MovieRepository', 'Word2VecMovieRecommender', 'KnnRecommender']

#Cell
import logging
import random
from typing import List, NamedTuple, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
from nbdev.showdoc import *
from tqdm import tqdm


#Cell
# constants
RANDOM_SEED = 31

logger = logging.getLogger(__name__)

#Cell
class GensimParameters(NamedTuple):
    window: int = 10
    iter: int = 20
    sg: int = 1
    hs: int = 0
    negative: int = 10
    alpha: float = 0.03
    min_alpha: float = 0.0007
    seed: int = 14
    compute_loss: bool = True

#Cell
def generate_sentences_by_user(df: pd.DataFrame):
    """
    Generate the Gensin sentences for a dataframe.
    Each sentence is created by joining all ratings from a user sorted by timestamp.
    """
    def to_sentence(r):
        return [str(m) for m in r]
    return df.groupby('userId')['movieId'].apply(to_sentence).tolist()

#Cell
class _EpochLogger(CallbackAny2Vec):
    """
    Log information about training, reports time for epochs.
    """
    def __init__(self, print_to_stdout: bool = False):
        """
        Constructor for the class to log progress information.
        """
        self._epoch = 1
        self._start = datetime.now()
        self._end = datetime.now()
        self._print_to_stdout = print_to_stdout

    def on_epoch_begin(self, _):
        """
        Print progress information, initializes start time.
        :param _: type gensim word2vec, signature to match the function to be used by gensim
        """
        self._start = datetime.now()
        msg = f"Epoch #{self._epoch} start"
        if self._print_to_stdout:
            print(msg)
        logger.info(msg)

    def on_epoch_end(self, model):
        """
        Print time to for epoch
        :param model: type gensim word2vec, signature to match the function to be used by gensim
        """
        self._end = datetime.now()
        elapsed = self._end - self._start
        msg = f"Epoch #{self._epoch} end in {elapsed} time"
        if self._print_to_stdout:
            print(msg)
        logger.info(msg)
        msg = f"Epoch #{self._epoch}, loss {model.get_latest_training_loss()}"
        if self._print_to_stdout:
            print(msg)
        logger.info(msg)
        self._epoch += 1


#Cell
class Recommendation(NamedTuple):
    movie_id: int
    score: float

#Cell
@dataclass
class Movie:
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
class Word2VecMovieRecommender:
    """
    This class encapsulates the training of recommendations plus utilities for persistance and predictions
    """
    def __init__(
        self,
        movies_df: pd.DataFrame,
        ratings_df: pd.DataFrame,
        gensim_parameters: GensimParameters,
        positive_rating_threshold: float = 3.0,
        train_validation_ratio: float = 0.9
        ):

        self.movies_df = movies_df
        self.ratings_df = ratings_df
        self.gensim_parameters = gensim_parameters
        self.model: Word2Vec = None

        # joins movie and ratings df
        df_joined = ratings_df.set_index('movieId').join(movies_df.set_index('movieId'), on='movieId', rsuffix='movie_').reset_index()
        # keep only positive ratings
        df_joined = df_joined[df_joined['rating'] >= positive_rating_threshold]
        # sort by user interactions
        df_joined.sort_values(by=['userId', 'timestamp'], inplace=True)
        # train validation split
        user_ids = df_joined["userId"].unique().tolist()
        random.Random(RANDOM_SEED).shuffle(user_ids)
        training_size = int(0.9 * len(user_ids))
        training_user_ids = user_ids[:training_size]
        validation_user_ids = user_ids[training_size:]
        assert len(validation_user_ids) + len(training_user_ids) == len(user_ids)
        self.train_df = df_joined[df_joined['userId'].isin(training_user_ids)]
        self.validation_df = df_joined[df_joined['userId'].isin(validation_user_ids)]


    def __repr__(self):
        return f"movies={self.movies_df.shape}, ratings={self.ratings_df.shape}, " +\
            f"train_df={self.train_df.shape}, validation_df={self.validation_df.shape}"

    def train(self, print_progress: bool = False):
        sentences_train = generate_sentences_by_user(self.train_df)
        self.model = Word2Vec(sentences_train, callbacks=[_EpochLogger(print_to_stdout=print_progress)],  **self.gensim_parameters._asdict())

    def similar_by_movie_id(self, seed_movie_id: int, n: int = 5) -> List[Recommendation]:
        movie_embedding = self.model.wv[str(seed_movie_id)]
        movies = self.model.wv.similar_by_vector(movie_embedding, topn= n+1)[1:]
        return [ Recommendation(movie_id=int(m[0]), score=m[1]) for m in movies ]

    def save_all(self, output_path: Path):
        if not output_path.exists():
            output_path.mkdir()
        if not output_path.is_dir():
            raise ValueError(f"{output_path} should be a directory")
        word_indexes = word2vec_recommender.model.wv.index2word
        embeddings = word2vec_recommender.model.wv.vectors
        with open(output_path / 'words_index.pkl', 'wb') as f:
            np.save(f, word_indexes)
        with open(output_path / 'embeddings.pkl', 'wb') as f:
            np.save(f, embeddings)


#Cell
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

class KnnRecommender:
    def __init__(
        self,
        word_indexes: List[str],
        embeddings: np.array,
        n_recommendations: int = 10,
        algorithm: str = 'brute'):

        self.word_indexes = word_indexes
        # https://stackoverflow.com/a/34145444 Normalize ensures euclidean will have the same output as cosine
        self.embeddings = normalize(embeddings)
        self._n_recommendations = n_recommendations
        self._algorithm = algorithm

        self.nn_model: NearestNeighbors = None

    def fit(self):
        self.nn_model = NearestNeighbors(n_neighbors=self._n_recommendations+1, algorithm=self._algorithm)
        self.nn_model.fit(self.embeddings)

    def recommend_by_index(self, index: int) -> List[Tuple[int, float]]:
        embedding = self.embeddings[index]
        istances_array, indexes_array = self.nn_model.kneighbors([embedding])
        recommendations = []
        for ind, dist in zip(indexes_array[0][1:], distances_array[0][1:]):
            recommendations.append( (int(self.word_indexes[ind]), dist))
        return recommendations
