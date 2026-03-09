# 1. Use a Node.js base image instead of Python
FROM node:18-slim

# 2. Install Chromium and all the required system libraries
RUN apt-get update && apt-get install -y \
    chromium \
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
    && rm -rf /var/lib/apt/lists/*

# 3. Setup the Node app
WORKDIR /bot
COPY bot/package*.json ./
RUN npm install
COPY bot/bot.js .

EXPOSE 8000

# 4. Start the bot
CMD ["node", "bot.js"]
