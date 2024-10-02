FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# DEV
CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0"]

# PROD
# CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0"]