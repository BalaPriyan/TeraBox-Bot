# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the bot script, requirements.txt, and config.env files into the container
COPY bot.py /app/bot.py
COPY requirements.txt /app/requirements.txt
COPY config.env /app/config.env

# Install necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot script
CMD ["python", "bot.py"]
