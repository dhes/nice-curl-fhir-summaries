import json, sys, os
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
if 'issue' in data:
    for i in data['issue']:
        print(i.get('severity', ''), i.get('diagnostics', i.get('details', {}).get('text', '')))
    sys.exit()

names = data.get('name', [{}])
n = names[0]
family = n.get('family', '-')
given = ' '.join(n.get('given', ['-']))
name_str = '%s, %s' % (family, given)

dob = data.get('birthDate', '-')
gender = data.get('gender', '-')
mrn = '-'
for ident in data.get('identifier', []):
    t = ident.get('type', {}).get('coding', [{}])[0].get('code', '')
    if t == 'MR':
        mrn = ident.get('value', '-')
        break

age_str = '-'
if dob != '-':
    try:
        born = date.fromisoformat(dob)
        today = date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        age_str = str(age)
    except:
        pass

addrs = data.get('address', [])
addr_str = '-'
if addrs:
    a = addrs[0]
    parts = a.get('line', [])
    city = a.get('city', '')
    state = a.get('state', '')
    postal = a.get('postalCode', '')
    addr_str = ', '.join(parts)
    if city:
        addr_str += ', %s' % city
    if state:
        addr_str += ', %s' % state
    if postal:
        addr_str += ' %s' % postal

phones = []
emails = []
for t in data.get('telecom', []):
    if t.get('system') == 'phone':
        phones.append(t.get('value', ''))
    elif t.get('system') == 'email':
        emails.append(t.get('value', ''))

lines = []
lines.append('=' * 60)
lines.append('  PATIENT DEMOGRAPHICS')
lines.append('=' * 60)
lines.append('  Name:      %s' % name_str)
lines.append('  DOB:       %s  (Age: %s)' % (dob, age_str))
lines.append('  Gender:    %s' % gender)
lines.append('  MRN:       %s' % mrn)
lines.append('  Address:   %s' % addr_str)
if phones:
    lines.append('  Phone:     %s' % ', '.join(phones))
if emails:
    lines.append('  Email:     %s' % ', '.join(emails))
lines.append('=' * 60)

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'demographics-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to demographics-output.txt')
