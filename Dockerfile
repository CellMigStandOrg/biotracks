FROM continuumio/miniconda3

# https://www.continuum.io/blog/developer-blog/anaconda-and-docker-better-together-reproducible-data-science
#  docker run -i -t -p 8888:8888 continuumio/anaconda3 /bin/bash -c "/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser"

RUN true \
	&& pip install --upgrade pip \
	&& conda install -y matplotlib \
	&& true

RUN true \
	&& apt-get update \
	&& apt-get install -y make \
	&& rm -rf /var/lib/apt/lists/* \
	&& true

COPY . /src
WORKDIR /src

RUN true \
	&& adduser dp \
	&& pip install -r requirements.txt \
	&& pip install pytest \
	&& python setup.py install \
	&& chown -R dp:dp /src \
	&& true

USER dp
CMD ["make", "test"]
