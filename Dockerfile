
FROM python:3.10.5-alpine3.16 as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN set -ex \
#   && apk add --no-cache --update \
#     openssh cargo \
#     bash git libffi-dev \
#     postgresql-dev libpq-dev \
#     postgresql-libs libc-dev \ 
#     gcc g++ 

COPY . /app/
COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# FROM python:3.10.12-alpine3.18 as release
FROM python:3.10-alpine as release

WORKDIR /app

RUN set -ex \
  && apk add --no-cache --update \
    libpq
    
    
# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache /wheels/*

EXPOSE 8000

COPY --chown=appuser:appuser --from=builder /app /app

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3","--timeout", "120", "mysite.wsgi:application"]