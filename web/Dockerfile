FROM python:3.10.4-slim@sha256:a2e8240faa44748fe18c5b37f83e14101a38dd3f4a1425d18e9e0e913f89b562

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install postgresql-client for healthchecking
RUN apt-get update && \
    apt-get install -y \
    	postgresql-client \
    	pandoc  \
    	texlive-latex-base \
    	texlive-fonts-recommended \
    	texlive-fonts-extra \
    	texlive-latex-extra && \
    apt-get autoremove && \
    apt-get autoclean

WORKDIR /worker
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY . /worker/
