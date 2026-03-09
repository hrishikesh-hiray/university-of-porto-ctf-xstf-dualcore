FROM node:22-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    g++ \
    make \
    tini \
    xvfb \
    chromium \
    mesa-utils \
    libgl1-mesa-dri \
    libxi6 \
    libgconf-2-4 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

RUN touch media.db && chmod 777 media.db

EXPOSE 6969

CMD ["node", "server.js"]
