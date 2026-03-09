FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AXEL_BIN=/usr/local/bin/axel

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    autoconf \
    autoconf-archive \
    automake \
    autopoint \
    gettext \
    libssl-dev \
    pkg-config \
    txt2man \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/axel-download-accelerator/axel.git /tmp/axel-src \
    && cd /tmp/axel-src \
    && autoreconf -i \
    && ./configure --disable-Werror \
    && make -j"$(nproc)" \
    && make install \
    && rm -rf /tmp/axel-src

RUN adduser --disabled-password --gecos '' appuser

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/
COPY templates /app/templates
COPY static /app/static
COPY files /app/files
COPY readFlag.c /tmp/readFlag.c

RUN gcc -o /readFlag /tmp/readFlag.c && rm /tmp/readFlag.c \
    && chmod 755 /readFlag
RUN chown -R appuser:appuser /app/files \
    && chmod -R 755 /app \
    && chmod 777 /app/files

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5006
CMD ["/entrypoint.sh"]
