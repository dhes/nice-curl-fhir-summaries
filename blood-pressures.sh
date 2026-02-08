#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "$FHIR_BASE_URL/Observation?patient=$FHIR_PATIENT_ID&code=85354-9&_sort=-date" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/blood-pressures.py"
