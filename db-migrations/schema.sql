BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS Users (
    id VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    passwd VARCHAR(255),
    picture TEXT,
    oauth_id VARCHAR(255) UNIQUE,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Movies (
    id VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY,
    download_path TEXT,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_watched TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    watched BOOLEAN NOT NULL DEFAULT TRUE,
    downloaded BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE UserMovies (
    movie_id VARCHAR(255),
    user_id VARCHAR(255),
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES Movies(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Comments (
    id VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comment TEXT NOT NULL,
    movie_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movies(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (author_id) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

COMMIT;