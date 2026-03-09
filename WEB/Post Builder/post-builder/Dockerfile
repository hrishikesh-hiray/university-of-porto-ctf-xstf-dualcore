FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    chromium \
    supervisor \
    # chromium-driver is REMOVED
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libx11-6 libx11-xcb1 libxcb1 libxcursor1 libxi6 libxtst6 \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/backend/ .

WORKDIR /app/frontend
COPY app/frontend/package*.json ./
RUN npm install
COPY app/frontend/ .

# --- THIS IS THE PART THAT CHANGES ---
WORKDIR /bot
COPY bot/package*.json ./
RUN npm install
COPY bot/bot.js .
# -------------------------------------

RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/log/nginx /var/log/supervisor /tmp/nginx_client_temp /tmp/nginx_proxy_temp /tmp/nginx_fastcgi_temp /tmp/nginx_uwsgi_temp /tmp/nginx_scgi_temp

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80 5001

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
