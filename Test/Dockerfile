FROM python:3.10-slim

# Установка системных зависимостей для сборки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем требования (уже с обновленным PyYAML)
COPY clean_requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r clean_requirements.txt

COPY . .

CMD ["python", "app.py"]