FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY clean_requirements.txt .

RUN pip install --no-cache-dir -r clean_requirements.txt

COPY . .

ENV TEST_TARGET_URL=http://127.0.0.1:8000/blog/home/
ENV PYTHONPATH=/app

CMD ["python", "runner.py"]