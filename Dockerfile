FROM python:3.8

RUN pip install snowflake-snowpark-python flask

COPY ./src /src

WORKDIR /src

EXPOSE 8001
CMD python app.py