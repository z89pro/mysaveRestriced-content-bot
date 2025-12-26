FROM python:3.10.8-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN dos2unix start.sh && chmod +x start.sh

EXPOSE 8000
CMD ["bash", "start.sh"]
