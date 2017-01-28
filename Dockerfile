FROM continuumio/miniconda3

# https://www.continuum.io/blog/developer-blog/anaconda-and-docker-better-together-reproducible-data-science
#  docker run -i -t -p 8888:8888 continuumio/anaconda3 /bin/bash -c "/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser"


RUN apt-get install make
RUN pip install --upgrade pip
RUN conda install -y matplotlib
RUN pip install datapackage jsontableschema jsontableschema-pandas
RUN pip install pytest
RUN adduser dp
COPY . /src
WORKDIR /src
RUN chown -R dp:dp /src
USER dp
RUN make test
