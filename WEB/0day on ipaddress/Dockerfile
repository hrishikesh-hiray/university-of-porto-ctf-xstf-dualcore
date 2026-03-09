FROM python:3.9-slim

RUN apt-get update

WORKDIR /app

COPY server.py /app
COPY requirements.txt /app
COPY nmap /app
COPY flag /app/flag
COPY xlag.txt /app/xlag.txt
COPY flag.tx /app/flag.tx
COPY /flag.php /app/flag.php
RUN chmod +x /app/nmap

RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/app:$PATH"

EXPOSE 5000

CMD ["python", "server.py"]
