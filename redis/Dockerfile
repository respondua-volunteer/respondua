FROM redis:7.2.0-alpine3.18

WORKDIR /redis

COPY redis.conf /usr/local/etc/redis/redis.conf

COPY init.sh ./

RUN chmod +x init.sh