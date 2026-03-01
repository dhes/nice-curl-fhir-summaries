#!/bin/zsh
# Fetch all colonoscopy DiagnosticReports with included Observations, Specimens, and Performers
curl -s -u "$FHIR_USER:$FHIR_PASS" \
  "$FHIR_BASE_URL/DiagnosticReport?patient=$FHIR_PATIENT_ID&code=11502-2&_sort=date&_include=DiagnosticReport:result&_include=DiagnosticReport:specimen&_include=DiagnosticReport:performer&_count=200" \
  -H 'Accept: application/fhir+json' | python3 "$(dirname "$0")/colonoscopy.py"
