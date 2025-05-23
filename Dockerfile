# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update -y && apt-get install wget -y

# Copy the current directory contents into the container
COPY . .

# Create a directory for logs
RUN mkdir -p /app/logs
COPY .env /app/.env
# Make port 5000 available to the world outside this container


# Run the Flask application
CMD ["gunicorn", "-w","2", "--bind","0.0.0.0:22001","app:app"]