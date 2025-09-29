FROM python:3.13-slim
WORKDIR /usr/local/app

ENV PYTHONUNBUFFERED=1

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "app.main"]