
FROM python:3.10.5-alpine3.16 AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


COPY . /app/
COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-alpine AS release

WORKDIR /app

RUN set -ex \
  && apk add --no-cache --update \
    libpq
    
    
# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    find /usr/local/lib/python3.10/site-packages -name '*.pyc' -delete && \
    find /usr/local/lib/python3.10/site-packages -name '__pycache__' -type d -exec rm -r {} + && \
    rm -rf /root/.cache /root/.pip


COPY --chown=appuser:appuser --from=builder /app /app

RUN install -d -o appuser -g appgroup /app/staticfiles \
 && install -d -o appuser -g appgroup /app/media \
 && install -d -o appuser -g appgroup /app/

COPY /entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]