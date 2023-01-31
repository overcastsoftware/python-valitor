FROM python:3.10

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt --src /usr/local/src
COPY . /code/
