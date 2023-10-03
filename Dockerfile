FROM python:3.12-alpine3.18
WORKDIR /
COPY requirements.txt .
RUN pip install  --no-cache-dir -r requirements.txt
WORKDIR /app
COPY src/ /app/

ENTRYPOINT [ "python", "gpx.py" ]
