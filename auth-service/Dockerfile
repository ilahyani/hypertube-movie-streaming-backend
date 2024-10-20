FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]