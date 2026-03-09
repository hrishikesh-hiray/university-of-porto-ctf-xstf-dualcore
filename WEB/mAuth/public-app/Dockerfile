FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY flag.txt .

RUN touch /tmp/app.log && chmod 666 /tmp/app.log

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--access-logfile", "/tmp/app.log", "--access-logformat", "%(t)s - %(r)s", "app:app"]
