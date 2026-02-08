#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "https://cds.hopena.info/fhir/Observation?patient=$FHIR_PATIENT_ID&code=18262-6,13457-7,2089-1&_sort=-date" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/ldl-values.py"
