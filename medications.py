import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No medication statements found.')
    sys.exit()

rows = []
for e in entries:
    r = e['resource']
    mc = r.get('medicationCodeableConcept', {})
    mr = r.get('medicationReference', {})
    coding = mc.get('coding', [{}])[0]
    display = coding.get('display', mc.get('text', mr.get('display', '-')))
    code = coding.get('code', '-')
    system = coding.get('system', '-')
    if 'rxnorm' in system.lower():
        system = 'RxNorm'
    elif 'ndc' in system.lower():
        system = 'NDC'
    elif 'snomed' in system.lower():
        system = 'SNOMED'
    period = r.get('effectivePeriod', {})
    start = period.get('start', r.get('effectiveDateTime', '-'))[:10]
    end = period.get('end', '-')[:10]
    status = r.get('status', '-')
    dosage = '-'
    dosages = r.get('dosage', [])
    if dosages:
        dosage = dosages[0].get('text', '-')
    if len(display) > 38:
        display = display[:37] + '...'
    rows.append((display, code, system, start, end, status, dosage))

status_order = {'active': 0, 'intended': 1, 'on-hold': 2, 'completed': 3, 'stopped': 4, 'not-taken': 5, 'entered-in-error': 6}
rows.sort(key=lambda r: (status_order.get(r[5], 9), r[3]))

lines = []
lines.append('%-40s %-12s %-8s %-12s %-12s %-10s %s' % ('Medication', 'Code', 'System', 'Start', 'End', 'Status', 'Dosage'))
lines.append('-' * 115)
for display, code, system, start, end, status, dosage in rows:
    lines.append('%-40s %-12s %-8s %-12s %-12s %-10s %s' % (display, code, system, start, end, status, dosage))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'medications-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to medications-output.txt')
