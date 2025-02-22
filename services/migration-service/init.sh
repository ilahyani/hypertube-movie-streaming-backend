#!/bin/bash

apt-get update && apt-get install -y postgresql-client

pip install python-dotenv psycopg[binary]

until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "$(date) - waiting for database to start"
  sleep 2
done

python3 /tmp/db/run_migration.py /tmp/db/schema.sql