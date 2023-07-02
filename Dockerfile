FROM cgr.dev/chainguard/python:3.11-dev AS builder

WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM cgr.dev/chainguard/python:3.11
COPY --from=builder /home/nonroot/.local/lib/python3.11/site-packages /home/nonroot/.local/lib/python3.11/site-packages

WORKDIR /app
COPY src/ /app/

ENTRYPOINT [ "python", "gpx.py" ]
