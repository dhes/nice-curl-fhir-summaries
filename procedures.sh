#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "$FHIR_BASE_URL/Procedure?patient=$FHIR_PATIENT_ID&_sort=-date&_count=100" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/procedures.py"
