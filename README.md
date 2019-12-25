# Tickets Calendar

The project is built to find the cheapest flight tickets using FastAPI, Uvicorn, PostgreSQL and Kiwi.com booking API

#### Running

1)Download the project and navigate to the folder

2)Launch RestAPI service, Postgres and Cron
```
sudo docker-compose build
sudo docker-compose up
```

wait until you see 'myproj_api_1  | INFO:     Application startup complete.'

#### Documentation

All requests can be found on http://localhost:5057/docs

DB: postgresql://localhost:54320/docker_db

The input date format should be: Y-M-D (2019-12-17)

For demonstration purposes the cron runs every 5 minutes (updates the data);
To make it run every day at 00:00, use the first line in hello.cron

#### Requirements

* Python3
    * required packages in requirements.txt
* Uvicorn
* FastAPI
* Docker
