CREATE DATABASE docker_db;
\connect docker_db
 CREATE TABLE IF NOT EXISTS flight_tickets (id serial PRIMARY KEY, fly_from varchar(3),fly_to varchar(3),dep_date date,price int,booking_token text UNIQUE,created_at timestamp, updated_at timestamp);