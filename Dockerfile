# Use the official Python image from the Docker Hub
FROM python:3.11.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirments.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirments.txt

# Copy the entire project into the container
COPY . .

# Expose the port the app runs on
EXPOSE 9090

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9090"]