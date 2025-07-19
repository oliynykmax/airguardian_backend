# Use an official Python runtime as a parent image.
# Using '-slim' results in a smaller image size.
FROM python:3.13.5-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the file with your Python package dependencies
COPY requirements.txt .

# Install the dependencies
RUN apt-get update && apt-get install -y curl iputils-ping && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Command to run your application. This will execute `python main.py`
# when the container starts.
CMD ["python", "main.py"]
