#!/bin/zsh
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  'https://cds.hopena.info/fhir/PractitionerRole?_count=100' \
  -H 'Accept: application/fhir+json' -o /tmp/practroles.json && \
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  'https://cds.hopena.info/fhir/Practitioner?_count=100&_sort=family' \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/practitioners.py"
