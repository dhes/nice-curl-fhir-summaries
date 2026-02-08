#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "https://cds.hopena.info/fhir/Patient/$FHIR_PATIENT_ID" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/demographics.py"
