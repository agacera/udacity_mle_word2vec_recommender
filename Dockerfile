FROM continuumio/miniconda3

RUN mkdir /app
WORKDIR /app

# configure conda # conda create --name env --file <this file> python=3.7
# install dependencies
ADD environment_dash.yml .
RUN conda env create --file environment_dash.yml python=3.7 && \
    echo "source activate recommender_dash" > ~/.bashrc
ENV PATH /opt/conda/envs/recommender_dash/bin:$PATH
ENV PYTHONPATH /app/word2vec_recommender:$PYTHONPATH
RUN conda init bash

# Add code and data
ADD word2vec_recommender .
ADD data .

EXPOSE 9898

CMD [ "bash", "-c", "python run_explorer.py"]