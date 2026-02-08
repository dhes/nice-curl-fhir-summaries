#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "https://cds.hopena.info/fhir/Observation?patient=$FHIR_PATIENT_ID&code=85354-9&_sort=-date" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/blood-pressures.py"
