# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install any dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy only the app directory from the local repository to the container
COPY app/ /app

# Expose the port your app runs on
EXPOSE 8000   

# Command to run the Flask app using Gunicorn (with WebSocket support if needed)
CMD ["gunicorn", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "--log-level", "debug", "--timeout", "30", "--bind", "0.0.0.0:8000", "app:app"]
