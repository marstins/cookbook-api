FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
RUN mkdir -p instance

ENV PYTHONPATH=src \
    FLASK_APP=app.app \
    PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["sh", "-c", "flask seed && flask run --host 0.0.0.0 --port 5000"]
