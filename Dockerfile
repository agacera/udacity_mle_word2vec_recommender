FROM continuumio/miniconda3

RUN mkdir /app
WORKDIR /app

# configure conda # conda create --name env --file <this file> python=3.7
# install dependencies
ADD environment.yml .
RUN conda env create --file environment.yml python=3.7 && \
    echo "source activate udacity_project" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
