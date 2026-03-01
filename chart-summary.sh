#!/bin/zsh
DIR="$(dirname "$0")"
OUTFILE="$DIR/chart-summary.txt"
DATE=$(date '+%Y-%m-%d')

echo "Generating chart summary..."
echo ""

# Run all individual scripts
echo "  Fetching demographics..."
"$DIR/demographics.sh" > /dev/null 2>&1

echo "  Fetching allergies..."
"$DIR/allergies.sh" > /dev/null 2>&1

echo "  Fetching problem list..."
"$DIR/problem-list.sh" > /dev/null 2>&1

echo "  Fetching medications..."
"$DIR/medications.sh" > /dev/null 2>&1

echo "  Fetching immunizations..."
"$DIR/immunizations.sh" > /dev/null 2>&1

echo "  Fetching procedures..."
"$DIR/procedures.sh" > /dev/null 2>&1

echo "  Fetching colonoscopy surveillance..."
"$DIR/colonoscopy.sh" > /dev/null 2>&1

echo "  Fetching family history..."
"$DIR/family-history.sh" > /dev/null 2>&1

echo "  Fetching care team..."
"$DIR/practitioners.sh" > /dev/null 2>&1

# Assemble the chart summary
{
  echo "========================================================================"
  echo "  PATIENT CHART SUMMARY"
  echo "  Generated: $DATE"
  echo "========================================================================"
  echo ""

  echo "--- DEMOGRAPHICS ---"
  cat "$DIR/demographics-output.txt"
  echo ""

  echo "--- ALLERGIES / INTOLERANCES ---"
  cat "$DIR/allergies-output.txt"
  echo ""

  echo "--- PROBLEM LIST ---"
  cat "$DIR/problem-list-output.txt"
  echo ""

  echo "--- MEDICATIONS ---"
  cat "$DIR/medications-output.txt"
  echo ""

  echo "--- IMMUNIZATIONS ---"
  cat "$DIR/immunizations-output.txt"
  echo ""

  echo "--- PROCEDURES ---"
  cat "$DIR/procedures-output.txt"
  echo ""

  echo "--- COLONOSCOPY SURVEILLANCE ---"
  cat "$DIR/colonoscopy-output.txt"
  echo ""

  echo "--- FAMILY HISTORY ---"
  cat "$DIR/family-history-output.txt"
  echo ""

  echo "--- CARE TEAM ---"
  cat "$DIR/practitioners-output.txt"
  echo ""

  echo "========================================================================"
  echo "  END OF CHART SUMMARY"
  echo "========================================================================"
} > "$OUTFILE"

echo ""
echo "Chart summary written to: $OUTFILE"
echo ""
cat "$OUTFILE"
