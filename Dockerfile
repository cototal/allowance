FROM python:3.12-slim

ENV FLASK_APP=wsgi:app
ENV APP_ENV=prod
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["sh", "-c", "flask init-db && exec gunicorn --bind 0.0.0.0:8000 wsgi:app"]
