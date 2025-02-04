CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS texts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(1024),
    link TEXT
);

CREATE TABLE IF NOT EXISTS chats_state(
    id bigint PRIMARY KEY,
    state TEXT NOT NULL,
    previous_state TEXT NOT NULL,
    json_state_info TEXT
);

CREATE TABLE IF NOT EXISTS student(
    id bigint PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    patronymic TEXT NOT NULL,
    group_number INT NOT NULL,
    department INT NOT NULL
);

CREATE TABLE IF NOT EXISTS teacher(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    patronymic TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    department INT NOT NULL
);