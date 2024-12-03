# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the app port
EXPOSE 4000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4000"]
