# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for SQLite database
RUN mkdir -p /app/data

# Copy the rest of the application's code into the container at /app
COPY . .

# Define environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Initialize and run database migrations
RUN flask db init || echo "Migration directory already exists"
RUN flask db migrate -m "Initial migration" || echo "Migration already exists"

# Run the application
CMD ["sh", "-c", "flask db upgrade && gunicorn --timeout 120 --keep-alive 5 --workers 4 --worker-class gevent -b 0.0.0:8001 main:app"]