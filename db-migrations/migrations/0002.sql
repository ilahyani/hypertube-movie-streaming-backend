-- add oauth_id

BEGIN;

INSERT INTO migrations (version, description) VALUES ('0002', 'added oauth_id');

ALTER TABLE users ADD oauth_id VARCHAR(255) UNIQUE;

COMMIT;