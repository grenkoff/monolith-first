#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

core="${CORE_URL:-http://localhost:8000}"
name="e2e-$RANDOM"

product="$(curl -fsS -X POST "$core/api/v1/catalog/products/" \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"$name\", \"price_cents\": 350}")"
id="$(echo "$product" | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')"
echo "product $id"

home="$(curl -fsS "$core/")"
if [[ "$home" != *"$name"* ]]; then
  echo "FAIL: the home page does not list the product"
  exit 1
fi
stylesheet="$(curl -fsS "$core/static/site/site.css")"
if [[ "$stylesheet" != *tailwindcss* ]]; then
  echo "FAIL: the stylesheet was not built by the Tailwind CLI"
  exit 1
fi
echo "OK: the home page lists the product, the stylesheet is built"

curl -fsS -X POST "$core/api/v1/orders/" \
  -H 'Content-Type: application/json' \
  -d "{\"product\": \"$id\", \"quantity\": 3}"
echo

for _ in $(seq 1 20); do
  if curl -fsS "$core/api/v1/catalog/products/$id/" | grep -q '"sold":3'; then
    echo "OK: the order went through orders -> outbox -> core-relay -> catalog"
    exit 0
  fi
  sleep 1
done

echo "FAIL: catalog did not learn about the order from the outbox"
docker compose logs core-relay | tail -20
exit 1
