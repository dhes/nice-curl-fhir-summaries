import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No LDL-C results found.')
    sys.exit()

lines = []
lines.append('%-12s %-10s %-10s %s' % ('Date', 'LDL-C', 'Unit', 'LOINC'))
lines.append('-' * 45)
for e in entries:
    o = e['resource']
    date = o.get('effectiveDateTime', '-')[:10]
    vq = o.get('valueQuantity', {})
    val = str(vq.get('value', '-'))
    unit = vq.get('unit', 'mg/dL')
    loinc = o.get('code', {}).get('coding', [{}])[0].get('code', '?')
    lines.append('%-12s %-10s %-10s %s' % (date, val, unit, loinc))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'ldl-values-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to ldl-values-output.txt')
