FROM python:3.13-slim
WORKDIR /usr/local/app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .env ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
EXPOSE 8000

CMD ["python", "src/main.py"]