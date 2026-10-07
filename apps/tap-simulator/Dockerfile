FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/tap-simulator"

WORKDIR /app

# Install dependencies
COPY apps/tap-simulator/requirements.txt /app/apps/tap-simulator/
RUN pip install --no-cache-dir -r /app/apps/tap-simulator/requirements.txt

# Copy shared contracts and simulator code
COPY contracts/ /app/contracts/
COPY apps/tap-simulator/ /app/apps/tap-simulator/

WORKDIR /app/apps/tap-simulator

CMD ["python", "main.py"]
