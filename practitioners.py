import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open('/tmp/practroles.json') as f:
    roles_data = json.load(f)
role_map = {}
for e in roles_data.get('entry', []):
    rr = e['resource']
    ref = rr.get('practitioner', {}).get('reference', '')
    specs = rr.get('specialty', [])
    if specs:
        spec = specs[0].get('coding', [{}])[0].get('display', '-')
        role_map[ref] = spec

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No practitioners found.')
    sys.exit()

rows = []
for e in entries:
    r = e['resource']
    rid = r.get('id', '-')
    active = 'yes' if r.get('active', False) else 'no'
    names = r.get('name', [{}])
    n = names[0]
    family = n.get('family', '-')
    given = ' '.join(n.get('given', ['-']))
    name_str = '%s, %s' % (family, given)
    specialty = role_map.get('Practitioner/%s' % rid, '-')
    rows.append((name_str, rid, active, specialty))

rows.sort(key=lambda r: (0 if r[2] == 'yes' else 1, r[0]))

lines = []
lines.append('%-30s %-35s %-8s %s' % ('Name', 'ID', 'Active', 'Specialty'))
lines.append('-' * 95)
for name_str, rid, active, specialty in rows:
    lines.append('%-30s %-35s %-8s %s' % (name_str, rid, active, specialty))

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'practitioners-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to practitioners-output.txt')
