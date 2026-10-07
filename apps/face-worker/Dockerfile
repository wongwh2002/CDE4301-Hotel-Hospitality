FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/face-worker" \
    PORT=8001

WORKDIR /app

# Install dependencies
COPY apps/face-worker/requirements.txt /app/apps/face-worker/
RUN pip install --no-cache-dir -r /app/apps/face-worker/requirements.txt

# Copy shared contracts, fixtures, and application code
COPY contracts/ /app/contracts/
COPY fixtures/ /app/fixtures/
COPY apps/face-worker/ /app/apps/face-worker/

WORKDIR /app/apps/face-worker

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
