#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "$FHIR_BASE_URL/Observation?patient=$FHIR_PATIENT_ID&code=18262-6,13457-7,2089-1&_sort=-date" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/ldl-values.py"
