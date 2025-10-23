FROM python:3.13-slim

# Create and set working directory
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Install dependencies + tools
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Copy entrypoint and make executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Use bash to execute the entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
