FROM python:3.10.8-slim-buster

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy all files
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Run the start script
CMD ["bash", "start.sh"]