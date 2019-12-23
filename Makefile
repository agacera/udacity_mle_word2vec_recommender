SRC = $(wildcard ./*.ipynb)

all: word2vec_movies_recommender docs
	nbdev_clean_nbs

word2vec_movies_recommender: $(SRC)
	nbdev_build_lib
	touch word2vec_movies_recommender

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

bump:
	nbdev_bump_version

dist: clean
	python setup.py sdist bdist_wheel

environment.yml:
	conda env export --no-builds > environment.yml

clean:
	rm -rf dist

PHONY: conda-env conda-remove-env

conda-env:
	conda env create --file environment_model.yml python=3.7

conda-remove-env:
	conda env remove -n word2vec_recommender