FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/mock-hotel" \
    PORT=8002

WORKDIR /app

# Install dependencies
COPY apps/mock-hotel/requirements.txt /app/apps/mock-hotel/
RUN pip install --no-cache-dir -r /app/apps/mock-hotel/requirements.txt

# Copy shared contracts, fixtures, and application code
COPY contracts/ /app/contracts/
COPY fixtures/ /app/fixtures/
COPY apps/mock-hotel/ /app/apps/mock-hotel/

RUN mkdir -p /data

WORKDIR /app/apps/mock-hotel

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
