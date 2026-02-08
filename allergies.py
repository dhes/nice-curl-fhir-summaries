import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No allergies/intolerances found.')
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
    elif 'rxnorm' in system.lower():
        system = 'RxNorm'
    elif 'ndfrt' in system.lower():
        system = 'NDF-RT'
    category = ', '.join(r.get('category', ['-']))
    clin_status = r.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', '-')
    ver_status = r.get('verificationStatus', {}).get('coding', [{}])[0].get('code', '-')
    criticality = r.get('criticality', '-')
    ai_type = r.get('type', '-')
    reactions = r.get('reaction', [])
    react_str = '-'
    if reactions:
        manifests = []
        for rx in reactions:
            for m in rx.get('manifestation', []):
                mt = m.get('coding', [{}])[0].get('display', m.get('text', ''))
                if mt:
                    manifests.append(mt)
        if manifests:
            react_str = ', '.join(manifests)

    if len(display) > 38:
        display = display[:37] + '...'
    if len(react_str) > 35:
        react_str = react_str[:34] + '...'
    rows.append((display, category, ai_type, criticality, clin_status, react_str))

status_order = {'active': 0, 'inactive': 1, 'resolved': 2}
rows.sort(key=lambda r: (status_order.get(r[4], 9), r[0]))

lines = []
lines.append('%-40s %-12s %-12s %-14s %-10s %s' % ('Substance', 'Category', 'Type', 'Criticality', 'Status', 'Reaction'))
lines.append('-' * 120)
for display, category, ai_type, criticality, clin_status, react_str in rows:
    lines.append('%-40s %-12s %-12s %-14s %-10s %s' % (display, category, ai_type, criticality, clin_status, react_str))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'allergies-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to allergies-output.txt')
