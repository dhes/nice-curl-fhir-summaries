#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "https://cds.hopena.info/fhir/Immunization?patient=$FHIR_PATIENT_ID&_sort=-date&_count=100" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/immunizations.py"
