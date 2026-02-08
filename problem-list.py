import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No conditions found.')
    sys.exit()

rows = []
for e in entries:
    r = e['resource']
    cc = r.get('code', {})
    coding = cc.get('coding', [{}])[0]
    display = coding.get('display', cc.get('text', '-'))
    code = coding.get('code', '-')
    system = coding.get('system', '-')
    if 'snomed' in system.lower():
        system = 'SNOMED'
    elif 'icd-10' in system.lower():
        system = 'ICD-10'
    elif 'icd-9' in system.lower():
        system = 'ICD-9'
    onset = r.get('onsetDateTime', r.get('onsetPeriod', {}).get('start', '-'))[:10]
    abate = r.get('abatementDateTime', r.get('abatementPeriod', {}).get('start', '-'))[:10]
    status = r.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', '-')
    if len(display) > 38:
        display = display[:37] + '...'
    rows.append((display, code, system, onset, abate, status))

status_order = {'active': 0, 'recurrence': 1, 'relapse': 2, 'inactive': 3, 'remission': 4, 'resolved': 5}
rows.sort(key=lambda r: (status_order.get(r[5], 9), r[3]))

lines = []
lines.append('%-40s %-12s %-12s %-12s %-12s %s' % ('Display', 'Code', 'System', 'Onset', 'Abatement', 'Status'))
lines.append('-' * 105)
for display, code, system, onset, abate, status in rows:
    lines.append('%-40s %-12s %-12s %-12s %-12s %s' % (display, code, system, onset, abate, status))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'problem-list-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to problem-list-output.txt')
