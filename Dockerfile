FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Copy requirements first for better caching
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the app directory
COPY ./app /app/app

# Copy main.py
COPY ./main.py /app/

# Set the working directory
WORKDIR /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Use the PORT environment variable from Cloud Run (default to 8080)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}