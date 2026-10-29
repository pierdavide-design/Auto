FROM node:18-slim

# Installazione dipendenze di sistema, Python e Chromium per Puppeteer
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    chromium \
    fonts-liberation \
    libasound2 \
    libnspr4 \
    libnss3 \
    libxss1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Copia e installa dipendenze Node.js
COPY whatsapp-service/package*.json ./whatsapp-service/
RUN cd whatsapp-service && npm install

# Copia e installa dipendenze Python con il flag esplicito
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copia tutto il progetto
COPY . .

# Avvio simultaneo di Node.js e del bot Python
CMD ["sh", "-c", "node whatsapp-service/server.js & python3 main.py"]