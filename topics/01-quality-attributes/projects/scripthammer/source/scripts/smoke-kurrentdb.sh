#!/usr/bin/env bash
# Writes and reads a synthetic event. Requires Docker, no local SDK.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

compose=(docker compose -p scripthammer-kurrent -f docker-compose.kurrent.yml)
event_id="$("${compose[@]}" exec -T kurrentdb cat /proc/sys/kernel/random/uuid)"
stream="scripthammer-smoke-${event_id}"
payload="[{\"eventId\":\"${event_id}\",\"eventType\":\"DockerSmokeTest\",\"data\":{\"marker\":\"${event_id}\"}}]"

"${compose[@]}" exec -T kurrentdb curl --fail --silent --show-error --connect-timeout 5 --max-time 20 \
    -H 'Content-Type: application/vnd.eventstore.events+json' \
    -H 'ES-ExpectedVersion: -1' \
    --data-binary "$payload" \
    "http://localhost:2113/streams/${stream}"

event="$("${compose[@]}" exec -T kurrentdb curl --fail --silent --show-error --connect-timeout 5 --max-time 20 \
    -H 'Accept: application/json' \
    "http://localhost:2113/streams/${stream}/0")"
case "$event" in
    *"${event_id}"*) printf 'PASS: wrote and read event in %s\n' "$stream" ;;
    *) printf 'FAIL: event read did not contain the expected marker\n' >&2; exit 1 ;;
esac
