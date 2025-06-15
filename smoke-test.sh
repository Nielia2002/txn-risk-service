#!/usr/bin/env bash
for i in $(seq 1 100); do
  curl -s -o /dev/null -w "%{http_code} " \
    -X POST http://localhost:8000/webhook/transaction \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d '{
      "transaction_id":"tx'"$i"'",
      "user_id":"load_test",
      "amount":'"$((RANDOM%100+1))"',
      "currency":"USD",
      "timestamp":"2025-06-14T16:00:00Z",
      "country":"US"
    }'
done
echo
