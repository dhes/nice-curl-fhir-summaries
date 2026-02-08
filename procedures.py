import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No procedures found.')
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
    elif 'cpt' in system.lower():
        system = 'CPT'
    elif 'hcpcs' in system.lower():
        system = 'HCPCS'
    elif 'icd-10' in system.lower():
        system = 'ICD-10-PCS'
    perf = r.get('performedDateTime', r.get('performedPeriod', {}).get('start', '-'))[:10]
    status = r.get('status', '-')
    if len(display) > 73:
        display = display[:72] + '...'
    rows.append((display, code, system, perf, status))

lines = []
lines.append('%-75s %-12s %-12s %-12s %s' % ('Display', 'Code', 'System', 'Date', 'Status'))
lines.append('-' * 125)
for display, code, system, perf, status in rows:
    lines.append('%-75s %-12s %-12s %-12s %s' % (display, code, system, perf, status))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'procedures-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to procedures-output.txt')
