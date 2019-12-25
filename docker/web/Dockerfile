FROM python:3.7-alpine
WORKDIR /home/myproj
COPY . / proj/
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev make
RUN pip install -U setuptools psycopg2
RUN pip install -r proj/requirements.txt