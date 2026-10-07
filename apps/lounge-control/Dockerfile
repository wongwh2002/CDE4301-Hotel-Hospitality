FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/lounge-control" \
    PORT=8000

WORKDIR /app

# Install dependencies
COPY apps/lounge-control/requirements.txt /app/apps/lounge-control/
RUN pip install --no-cache-dir -r /app/apps/lounge-control/requirements.txt

# Copy shared contracts, fixtures, and application code
COPY contracts/ /app/contracts/
COPY fixtures/ /app/fixtures/
COPY apps/lounge-control/ /app/apps/lounge-control/

WORKDIR /app/apps/lounge-control

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
