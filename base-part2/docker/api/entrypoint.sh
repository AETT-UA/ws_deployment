#!/bin/bash
RETRIES=40

until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
  sleep 5
done

echo "Connected to database!"

python3 manage.py makemigrations api
python3 manage.py migrate
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application --log-level debug