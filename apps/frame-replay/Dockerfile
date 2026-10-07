FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/frame-replay"

WORKDIR /app

# Install dependencies
COPY apps/frame-replay/requirements.txt /app/apps/frame-replay/
RUN pip install --no-cache-dir -r /app/apps/frame-replay/requirements.txt

# Copy shared contracts, fixtures, and replay code
COPY contracts/ /app/contracts/
COPY fixtures/ /app/fixtures/
COPY apps/frame-replay/ /app/apps/frame-replay/

WORKDIR /app/apps/frame-replay

ENTRYPOINT ["python", "main.py"]
CMD []
