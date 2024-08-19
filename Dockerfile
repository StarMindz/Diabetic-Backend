# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    postgresql \
    postgresql-contrib \
    python3-psycopg2 \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt


# Copy the rest of the application code to the container
COPY . /app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", ]
CMD ["sudo apt install python3-dev postgresql postgresql-contrib python3-psycopg2 libpq-dev"]
