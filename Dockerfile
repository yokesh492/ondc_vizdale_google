# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variable to store Cloud SQL credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/ONDC_GCP.json

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Use an entrypoint script to make use of Google Cloud's automatically provided $PORT
ENTRYPOINT ["sh", "-c"]
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT

