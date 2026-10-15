FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/face-worker" \
    FACE_MODELS_DIR="/models/insightface" \
    PORT=8001

WORKDIR /app

# InsightFace declares the regular OpenCV wheel as a dependency. Install its
# runtime dependencies from the headless list, then install the package itself
# without dependencies to avoid bringing in a conflicting GUI OpenCV wheel.
COPY apps/face-worker/requirements.txt /app/apps/face-worker/
RUN pip install --no-cache-dir -r /app/apps/face-worker/requirements.txt
RUN pip install --no-cache-dir --no-deps insightface==2.1.0

# Model weights are downloaded by InsightFace on first startup into a dedicated
# Compose volume; they are not copied into the source tree or image.
RUN mkdir -p /models

# Copy shared contracts, fixtures, and application code
COPY contracts/ /app/contracts/
COPY fixtures/ /app/fixtures/
COPY apps/face-worker/ /app/apps/face-worker/

WORKDIR /app/apps/face-worker

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
