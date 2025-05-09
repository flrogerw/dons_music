FROM python:3.11-alpine

RUN mkdir /app
RUN mkdir -p /app/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 3000
CMD ["python3", "/app/app.py"]