import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No blood pressures found.')
    sys.exit()

lines = []
lines.append('%-12s %-12s %s' % ('Date', 'Systolic', 'Diastolic'))
lines.append('-' * 38)
for e in entries:
    o = e['resource']
    date = o.get('effectiveDateTime', '-')[:10]
    sys_val = dia_val = 0
    for c in o.get('component', []):
        code = c['code']['coding'][0]['code']
        if code == '8480-6':
            sys_val = c['valueQuantity']['value']
        elif code == '8462-4':
            dia_val = c['valueQuantity']['value']
    if sys_val > 0 and dia_val > 0:
        lines.append('%-12s %-12s %s' % (date, sys_val, dia_val))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'blood-pressures-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to blood-pressures-output.txt')
