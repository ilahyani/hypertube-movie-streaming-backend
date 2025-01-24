BEGIN;

-- movies-users many to many relationship
-- comments-movies one to many relationship

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    passwd VARCHAR(255),
    picture TEXT,
    oauth_id VARCHAR(255) UNIQUE,
);

CREATE TABLE IF NOT EXISTS movies (
    id INT,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_watched TIMESTAMP NOT NULL,
    watched BOOLEAN NOT NULL DEFAULT TRUE
    downloaded BOOLEAN NOT NULL DEFAULT TRUE,
);

CREATE TABLE IF NOT EXISTS comments (
    id VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    movie_id 
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    comment TEXT,
);

COMMIT;