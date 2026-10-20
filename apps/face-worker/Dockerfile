FROM python:3.14-slim AS opencv-jxl-builder

ENV ENABLE_HEADLESS=1 \
    CMAKE_ARGS="-DWITH_JPEGXL=ON" \
    CMAKE_BUILD_PARALLEL_LEVEL=4

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libjxl-dev \
    ninja-build \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /wheelhouse && \
    python -m pip wheel --no-cache-dir --no-deps \
      --no-binary=opencv-python-headless \
      --wheel-dir=/wheelhouse \
      opencv-python-headless==4.14.0.94

FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/apps/face-worker" \
    FACE_MODELS_DIR="/models/insightface" \
    PORT=8001

WORKDIR /app

# The custom OpenCV wheel links to the system libjxl runtime libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjxl0.11 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=opencv-jxl-builder /wheelhouse /tmp/opencv-wheelhouse

# InsightFace declares the regular OpenCV wheel as a dependency. Install its
# runtime dependencies from the headless list, then install the package itself
# without dependencies to avoid bringing in a conflicting GUI OpenCV wheel.
COPY apps/face-worker/requirements.txt /app/apps/face-worker/
RUN pip install --no-cache-dir -r /app/apps/face-worker/requirements.txt && \
    pip install --no-cache-dir --no-deps --force-reinstall --no-index \
      --find-links=/tmp/opencv-wheelhouse \
      opencv-python-headless==4.14.0.94 && \
    rm -rf /tmp/opencv-wheelhouse
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
