import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No PSA results found.')
    sys.exit()

lines = []
lines.append('%-12s %-10s %s' % ('Date', 'PSA', 'Unit'))
lines.append('-' * 35)
for e in entries:
    o = e['resource']
    date = o.get('effectiveDateTime', '-')[:10]
    vq = o.get('valueQuantity', {})
    val = str(vq.get('value', '-'))
    unit = vq.get('unit', 'ng/mL')
    lines.append('%-12s %-10s %s' % (date, val, unit))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'psa-values-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to psa-values-output.txt')
