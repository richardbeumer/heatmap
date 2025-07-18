FROM python:3.13-alpine3.20
WORKDIR /
COPY requirements.txt .
RUN pip install  --no-cache-dir -r requirements.txt
WORKDIR /app
COPY src/ /app/

ENTRYPOINT [ "python", "gpx.py" ]
