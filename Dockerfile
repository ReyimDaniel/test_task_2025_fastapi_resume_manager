FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/certs

EXPOSE 8000

CMD ["uvicorn", "app_v1.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
