#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

core="${CORE_URL:-http://localhost:8000}"
name="e2e-$RANDOM"
url="$core/api/v1/greetings/"

echo "POST $url"
response="$(curl -fsS -X POST "$url" \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"$name\", \"polite\": true}")"
echo "$response"

expected="Hello, $name! Nice to meet you."
if [[ "$response" != *"$expected"* ]]; then
  echo "FAIL: core did not return the greeting from hello"
  exit 1
fi

received=""
for _ in $(seq 1 20); do
  if docker compose logs core-events 2>/dev/null | grep -q "$name"; then
    received="yes"
    break
  fi
  sleep 1
done
if [[ -z "$received" ]]; then
  echo "FAIL: core-events did not receive the hello.v1.greeted event"
  docker compose logs core-events | tail -20
  exit 1
fi
echo "OK: the greeting went through core -> hello -> nats -> core-events"

product="$(curl -fsS -X POST "$core/api/v1/catalog/products/" \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"$name\", \"price_cents\": 350}")"
id="$(echo "$product" | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')"
echo "product $id"

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
