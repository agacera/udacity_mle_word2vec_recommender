#AUTOGENERATED! DO NOT EDIT! File to edit: dev/04_explorer.ipynb (unless otherwise specified).

__all__ = ['create_dash_app']

#Cell
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from functools import lru_cache
from pathlib import Path

import pandas as pd
import numpy as np
import requests

from .core import *
from .recommender import KnnRecommender
from .tmdb import load_api_key, TmdbApi, MovieData

#Cell
def create_dash_app(dataset_path: Path, model_path: Path, dash_params: dict = None):
    # load dataframes
    movies_df = pd.read_csv(dataset_path / "movies.csv")
    links_df = pd.read_csv(dataset_path / "links.csv")

    # create TMDB API
    movielens_to_tmdb_lookup = {
        int(movie_id):int(tmdb_id)
        for movie_id, tmdb_id in links_df.set_index("movieId")["tmdbId"].to_dict().items()
        if movie_id > 0 and tmdb_id > 0
    }
    api = TmdbApi(api_key=load_api_key(), movielens_to_tmdb_lookup=movielens_to_tmdb_lookup)

    # load model
    with open(model_path / "embeddings.pkl", "rb") as f:
        embeddings = np.load(f)
    with open(model_path / "words_index.pkl", "rb") as f:
        word_indexes = np.load(f)
    movie_id_to_index_lookup = {int(movie_id):idx for idx, movie_id in enumerate(word_indexes)}
    knn_recommender = KnnRecommender(
        word_indexes=word_indexes,
        embeddings=embeddings)

    if not dash_params:
        dash_params={}
    app = dash.Dash(__name__, **dash_params)

    # base layout
    app.layout = html.Div(children=[
        html.H1(children='MovieLens Recommender based on Word2Vec'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),
        dcc.Dropdown(
            id="movie-id",
            options=movies_df[["title", "movieId"]].apply(lambda r:  {"value": r["movieId"], "label": r["title"]} ,axis=1).tolist(),
        ),
        html.Div(id="selected-movie-id", children="")
    ])

    def movie_card(movie: MovieData, seed: bool = False) -> html.Div:
        description = f"{movie.title} (id={movie.movie_id}, tmdb_id={movie.tmdb_id})"
        return html.Div(children=[
            html.H2(description) if seed else html.H3(description),
            html.Img(src=movie.image_url)
        ])

    @app.callback(
        Output(component_id='selected-movie-id', component_property='children'),
        [Input(component_id='movie-id', component_property='value')]
    )
    def update_output_div(movie_id) -> html.Div:
        if not movie_id:
            return html.Div(children="No movie selected")
        print(movie_id)
        movie = api.fetch_movie_data_by_movielens_id(int(movie_id))
        if not movie:
            return html.Div(children="Movie not found on TMDB")
        movie_index = movie_id_to_index_lookup.get(int(movie_id))
        if not movie_index:
            return html.Div(children="No embeddings for movie")
        movie_recs = knn_recommender.recommend_by_index(movie_index) or []
        movies = [ api.fetch_movie_data_by_movielens_id(rec.movie_id) for rec in movie_recs ]
        return html.Div(children=[
            movie_card(movie, seed=True),
            html.Div(children=[
                html.H2("Recommendations"),
                *[movie_card(m) for m in movies]
                ])
            ])

    return app