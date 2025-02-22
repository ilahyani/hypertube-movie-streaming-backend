FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt .

COPY ./entrypoint.sh .

RUN pip install --no-cache-dir -r ./requirements.txt

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]