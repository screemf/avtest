FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libffi-dev \
        libssl-dev \
        curl \
        wget \
        unzip \
        gnupg \
        jq \
        # Зависимости для Chrome
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libc6 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libexpat1 \
        libfontconfig1 \
        libgbm1 \
        libgcc1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libstdc++6 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        lsb-release \
        xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Установка последней стабильной версии Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Установка соответствующей версии ChromeDriver
RUN CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}') && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
    jq -r '.channels.Stable.version') && \
    echo "Устанавливаем ChromeDriver версии: $CHROMEDRIVER_VERSION (для Chrome $CHROME_VERSION)" && \
    wget -O /tmp/chromedriver.zip \
    "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

WORKDIR /app

# Сначала копируем только requirements.txt для лучшего кэширования
COPY clean_requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r clean_requirements.txt

# Копируем остальные файлы
COPY . .

ENV TEST_TARGET_URL=http://127.0.0.1:8000/blog/home/ \
    PYTHONPATH=/app \
    PATH="/usr/local/bin:${PATH}" \
    # Для headless Chrome
    DISPLAY=:99 \
    CHROME_BIN=/usr/bin/google-chrome-stable \
    CHROMEDRIVER_PATH=/usr/local/bin/chromedriver \
    # Оптимизация для Selenium
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

CMD ["python", "runner.py"]