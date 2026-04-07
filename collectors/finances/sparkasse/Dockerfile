# Use a small, official Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
# Copy the script into the container
COPY process.py .

# Run the script when the container starts
CMD ["python", "process.py"]
