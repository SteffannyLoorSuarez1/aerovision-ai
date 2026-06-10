FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install nicegui requests pandas

CMD ["python", "app.py"]