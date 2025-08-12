#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker-compose >/dev/null 2>&1; then
  echo 'Error: docker-compose is not installed.' >&2
  exit 1
fi

# >>> УКАЖИ НУЖНЫЕ ДОМЕНЫ <<<
# Для dev только: domains=(dev.respondua.org)
# Для prod+dev:  domains=(respondua.org dev.respondua.org)
domains=(dev.respondua.org)

rsa_key_size=4096
data_path="./docker/nginx/certbot"
email="volunteervolunteer245@gmail.com"   # замени при желании
staging=0                                  # 1 — тестовый режим (не трать лимит LE)

# Предупреждение при наличии старых данных
if [ -d "$data_path" ]; then
  read -p "Existing data found for ${domains[*]}. Replace existing certificates? (y/N) " decision
  if [[ "$decision" != "Y" && "$decision" != "y" ]]; then
    exit 0
  fi
fi

# Рекомендованные TLS параметры
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

# Временные (dummy) сертификаты для каждого домена, чтобы nginx стартанул
echo "### Creating dummy certificates ..."
for domain in "${domains[@]}"; do
  live_path="/etc/letsencrypt/live/$domain"
  mkdir -p "$data_path/conf/live/$domain"
  docker-compose run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:1024 -days 1 \
      -keyout '$live_path/privkey.pem' \
      -out '$live_path/fullchain.pem' \
      -subj '/CN=localhost'" certbot
done
echo

echo "### Starting nginx ..."
docker-compose up --force-recreate -d nginx
echo

# Удаляем dummy и запрашиваем реальные сертификаты по каждому домену
for domain in "${domains[@]}"; do
  echo "### Deleting dummy certificate for $domain ..."
  docker-compose run --rm --entrypoint "\
    rm -Rf /etc/letsencrypt/live/$domain && \
    rm -Rf /etc/letsencrypt/archive/$domain && \
    rm -Rf /etc/letsencrypt/renewal/$domain.conf" certbot
  echo

  echo "### Requesting Let's Encrypt certificate for $domain ..."
  # email arg
  if [ -z "$email" ]; then email_arg="--register-unsafely-without-email"; else email_arg="--email $email"; fi
  # staging arg
  if [ "$staging" != "0" ]; then staging_arg="--staging"; else staging_arg=""; fi

  docker-compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
      $staging_arg \
      $email_arg \
      -d $domain \
      --rsa-key-size $rsa_key_size \
      --agree-tos \
      --force-renewal" certbot
  echo
done

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload
echo "Done."
