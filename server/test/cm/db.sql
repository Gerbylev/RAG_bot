CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS texts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(1024),
    link TEXT
);


CREATE TABLE IF NOT EXISTS chat_state(
    id bigint PRIMARY KEY,
    state TEXT NOT NULL,
    json_state_info TEXT
);