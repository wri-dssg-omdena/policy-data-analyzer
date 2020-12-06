# Use the official miniconda3 alpine image as a parent image
FROM continuumio/miniconda3:4.9.2-alpine

# Changing user to root
USER root

# Install system dependencies
RUN apk --no-cache add \
    build-base \
    poppler-utils \
    swig \
    tesseract-ocr \
    tesseract-ocr-data-spa \
    tini

# Generate the en_US.UTF-8 locale and setting it (required by jamspell. See https://github.com/bakwc/JamSpell/issues/17)
RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
    && wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.32-r0/glibc-i18n-2.32-r0.apk \
    && apk add glibc-i18n-2.32-r0.apk \
    && /usr/glibc-compat/bin/localedef -i en_US -f UTF-8 en_US.UTF-8
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# Programs will be executed under Tini
ENTRYPOINT ["/sbin/tini", "--"]

# Defaults for executing the container (will be executed under Tini)
CMD ["sh", "--login", "-i"]
#CMD ["sh", "--login", "-ci", "jupyter notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
#jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root

# Set default shell as login shell
SHELL ["sh", "--login", "-c"]

# Define the workspace
WORKDIR /home/anaconda/project

# Copy repository with user access and pip install requirements into policy environment
COPY --chown=anaconda . .
RUN conda activate base \
    && pip install -r requirements.txt

# Changing back to default user. See https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b
USER anaconda
#
# ----------------------------------------------------------------------------------------------------------------------
## Use the official miniconda3 ubuntu image as a parent image
#FROM continuumio/miniconda3:4.9.2
#
## Install system dependencies
#RUN apt-get update && apt-get install -y \
#    build-essential \
##    libtesseract-dev \
##    libleptonica-dev \
##    pkg-config \
#    poppler-utils \
#    swig3.0 \
#    tesseract-ocr-spa \
#    && rm -rf /var/lib/apt/lists/*
#
## Create the policy conda environment
#RUN conda create -y -n policy python=3.8
#
## Define the workspace
#WORKDIR /root/project
#
## pip install requirements into policy environment
#COPY . .
#RUN /bin/bash -c "source activate policy \
#    && pip install -r requirements.txt"
# ----------------------------------------------------------------------------------------------------------------------
## Use the official alpine image as a parent image
#FROM alpine:latest
#
## Install system dependencies
#RUN apk add --update-cache \
#    build-base \
#    poppler-utils \
#    swig \
#    tesseract-ocr \
#    wget \
#    && rm -rf /var/cache/apk/*
#
## Install miniconda3
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#    && mkdir root/.conda \
#    && sh Miniconda3-latest-Linux-x86_64.sh -b \
#    && rm -f Miniconda3-latest-Linux-x86_64.sh
#
## Create the policy conda environment
#RUN conda create -y -n policy python=3.8
#
## Define the workspace
#WORKDIR /root/project
#
## pip install requirements into policy environment
#COPY . .
#RUN /bin/sh -c "source activate policy \
#    && pip install -r requirements.txt"
# ----------------------------------------------------------------------------------------------------------------------