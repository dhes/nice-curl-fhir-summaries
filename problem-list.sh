#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "$FHIR_BASE_URL/Condition?patient=$FHIR_PATIENT_ID&_sort=-onset-date&_count=100" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/problem-list.py"
