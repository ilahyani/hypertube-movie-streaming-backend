#!/bin/bash

apt-get update && apt-get install -y postgresql-client

until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "$(date) - waiting for database to start"
  sleep 2
done

python3 src/database/apply_migration.py src/database/migrations
fastapi dev src/main.py --host 0.0.0.0