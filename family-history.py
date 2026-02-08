import json, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No family history records found.')
    sys.exit()

output = []
for e in entries:
    r = e['resource']
    rid = r.get('id', '?')
    status = r.get('status', '-')
    name = r.get('name', '-')
    rel = r.get('relationship', {}).get('coding', [{}])[0].get('display', '-')
    sex = r.get('sex', {}).get('coding', [{}])[0].get('display', '-') if r.get('sex') else '-'
    born = r.get('bornDate', r.get('bornPeriod', {}).get('start', '-'))
    deceased = r.get('deceasedBoolean', None)
    deceased_date = r.get('deceasedDate', r.get('deceasedAge', {}).get('value', None))
    if deceased_date:
        dec_str = str(deceased_date)
    elif deceased is True:
        dec_str = 'yes'
    elif deceased is False:
        dec_str = 'no'
    else:
        dec_str = '-'

    output.append('')
    output.append('=' * 60)
    output.append('  %s (%s)  [id: %s]' % (name, rel, rid))
    output.append('  Sex: %s   Born: %s   Deceased: %s' % (sex, born, dec_str))
    output.append('  Status: %s' % status)

    conditions = r.get('condition', [])
    if conditions:
        output.append('  %-80s %-12s %-10s %-12s %s' % ('Condition', 'Code', 'System', 'Onset', 'Outcome'))
        output.append('  ' + '-' * 120)
        for c in conditions:
            cc = c.get('code', {})
            coding = cc.get('coding', [{}])[0]
            display = coding.get('display', cc.get('text', '-'))
            code = coding.get('code', '-')
            system = coding.get('system', '-')
            if 'snomed' in system.lower():
                system = 'SNOMED'
            elif 'icd-10' in system.lower():
                system = 'ICD-10'
            onset_age = c.get('onsetAge', {})
            onset_str = '-'
            if onset_age.get('value') is not None:
                onset_str = 'age %s' % int(onset_age['value'])
            elif c.get('onsetString'):
                onset_str = c['onsetString']
            outcome = c.get('outcome', {}).get('coding', [{}])[0].get('display', c.get('outcome', {}).get('text', '-'))
            if len(display) > 78:
                display = display[:77] + '...'
            output.append('  %-80s %-12s %-10s %-12s %s' % (display, code, system, onset_str, outcome))
    else:
        output.append('  (no conditions listed)')

result = '\n'.join(output)
print(result)

with open(os.path.join(SCRIPT_DIR, 'family-history-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to family-history-output.txt')
