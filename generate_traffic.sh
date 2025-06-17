#!/usr/bin/env bash
# ./generate_traffic.sh

URL="http://localhost:8002/webhook/transaction"
API_KEY="supersecret123"

# A small list of currencies & countries to randomize by label
CURRENCIES=(USD EUR GBP INR LKR BTC)
COUNTRIES=(US GB IN IN LK RU CN BR ZA)

for i in {1..500}; do
  txid="tx$(date +%s%N | cut -b1-13)-$i"
  amount=$(awk -v min=0.01 -v max=500 'BEGIN{srand(); printf "%.2f", min+rand()*(max-min)}')
  currency=${CURRENCIES[$RANDOM % ${#CURRENCIES[@]}]}
  country=${COUNTRIES[$RANDOM % ${#COUNTRIES[@]}]}
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  read -r -d '' PAYLOAD <<EOF
{
  "transaction_id": "${txid}",
  "user_id":        "user${i}",
  "amount":         ${amount},
  "currency":       "${currency}",
  "timestamp":      "${timestamp}",
  "country":        "${country}"
}
EOF

  curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$URL" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "$PAYLOAD" \
  && echo " ✔ $txid"
  
  # throttle a bit every 50 requests so you don’t slam the service
  if (( i % 50 == 0 )); then sleep 1; fi
done
