import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No immunizations found.')
    sys.exit()

rows = []
for e in entries:
    r = e['resource']
    vc = r.get('vaccineCode', {})
    coding = vc.get('coding', [{}])[0]
    display = coding.get('display', vc.get('text', '-'))
    code = coding.get('code', '-')
    system = coding.get('system', '-')
    if 'cvx' in system.lower():
        system = 'CVX'
    elif 'snomed' in system.lower():
        system = 'SNOMED'
    elif 'ndc' in system.lower():
        system = 'NDC'
    date = r.get('occurrenceDateTime', r.get('occurrenceString', '-'))[:10]
    status = r.get('status', '-')
    lot = r.get('lotNumber', '-')
    site = r.get('site', {}).get('coding', [{}])[0].get('display', '-')
    if len(display) > 73:
        display = display[:72] + '...'
    rows.append((date, display, code, system, status, lot, site))

rows.sort(key=lambda r: r[0], reverse=True)

lines = []
lines.append('%-12s %-75s %-10s %-8s %-12s %-15s %s' % ('Date', 'Vaccine', 'Code', 'System', 'Status', 'Lot', 'Site'))
lines.append('-' * 155)
for date, display, code, system, status, lot, site in rows:
    lines.append('%-12s %-75s %-10s %-8s %-12s %-15s %s' % (date, display, code, system, status, lot, site))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'immunizations-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to immunizations-output.txt')
