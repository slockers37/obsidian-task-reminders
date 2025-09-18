
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set UV_CACHE_DIR to a writable location
ENV UV_CACHE_DIR=/app/.uv_cache

# Install uv
RUN pip install uv

# Copy the requirements files to the container
COPY pyproject.toml uv.lock /app/

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code to the container
COPY src/ /app/src/

# Create data directory
RUN mkdir -p /app/data

# Switch to user 1000
USER 1000

# Set the command to run the application
CMD ["uv", "run", "src/main.py"]
