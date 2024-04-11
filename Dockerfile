FROM python:3.8

CMD pip install -y snowflake-snowpark-python flask

COPY ./src /src

WORKDIR = /src