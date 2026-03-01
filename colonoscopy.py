import json, sys, os
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

data = json.load(sys.stdin)
entries = data.get('entry', [])
if not entries:
    print('No colonoscopy data found.')
    sys.exit()

# ── Index all resources by fullUrl and by resourceType/id ──────────────
by_url = {}
drs = []
for e in entries:
    r = e['resource']
    rt = r.get('resourceType', '')
    rid = r.get('id', '')
    full = e.get('fullUrl', '')
    by_url[full] = r
    # also index by ResourceType/id for bare references
    by_url[f"{rt}/{rid}"] = r
    if rt == 'DiagnosticReport':
        drs.append(r)

# ── SNOMED → short histology abbreviation ──────────────────────────────
HISTO = {
    '444408007': 'TA',    # tubular adenoma
    '89452002':  'HP',    # hyperplastic polyp
    '1230009008':'SSP',   # sessile serrated polyp
    '309084001': 'VA',    # villous adenoma (colon)
    '312823001': 'VA',    # villous adenoma (rectum)
    '448428002': 'TVA',   # tubulovillous adenoma
    '721692006': 'BLP',   # benign lymphoid polyp
    '269533000': 'CA',    # carcinoma
    '68534000':  'MF',    # normal finding / mucosal fold
}

ADENOMA_CODES = {'TA', 'VA', 'TVA', 'SSP'}

def resolve_ref(ref_str):
    """Resolve a FHIR reference string to its resource."""
    if not ref_str:
        return None
    # try full URL first, then bare reference
    return by_url.get(ref_str) or by_url.get(ref_str.split('/')[-2] + '/' + ref_str.split('/')[-1] if '/' in ref_str else ref_str)

def get_ref(obj, key):
    """Get a reference string from a resource field."""
    ref_field = obj.get(key)
    if isinstance(ref_field, list):
        refs = []
        for item in ref_field:
            r = item.get('reference', '') if isinstance(item, dict) else ''
            refs.append(r)
        return refs
    elif isinstance(ref_field, dict):
        return [ref_field.get('reference', '')]
    return []

def extract_observation(obs):
    """Extract polyp details from an Observation resource."""
    info = {}
    # histology from valueCodeableConcept
    vcc = obs.get('valueCodeableConcept', {})
    codings = vcc.get('coding', [])
    if codings:
        code = codings[0].get('code', '')
        info['histo_code'] = code
        info['histo'] = HISTO.get(code, codings[0].get('display', code)[:6])
        info['histo_display'] = codings[0].get('display', '')
    else:
        info['histo'] = '?'
        info['histo_code'] = ''
        info['histo_display'] = ''

    # components: size, dysplasia, piecemeal, malignancy
    info['size_mm'] = None
    info['dysplasia'] = False
    info['piecemeal'] = False
    info['malignancy'] = False  # True means "no evidence of malignancy" (the boolean value)
    for comp in obs.get('component', []):
        comp_code = comp.get('code', {}).get('coding', [{}])[0].get('code', '')
        if comp_code == '21889-1':  # LOINC polypSize
            vq = comp.get('valueQuantity', {})
            info['size_mm'] = vq.get('value')
        elif comp_code == '55237006':  # SNOMED dysplasia
            info['dysplasia'] = comp.get('valueBoolean', False)
        elif comp_code == '787139004':  # SNOMED piecemeal
            info['piecemeal'] = comp.get('valueBoolean', False)
        elif comp_code == '110396000':  # SNOMED no malignancy
            info['malignancy'] = comp.get('valueBoolean', True)

    # specimen → body site
    spec_refs = get_ref(obs, 'specimen')
    info['site'] = ''
    info['site_display'] = ''
    if spec_refs:
        spec = resolve_ref(spec_refs[0])
        if spec:
            bs = spec.get('collection', {}).get('bodySite', {})
            info['site_display'] = bs.get('text', '')
            if not info['site_display']:
                bs_codings = bs.get('coding', [])
                info['site_display'] = bs_codings[0].get('display', '') if bs_codings else ''
            # shorten common body site names
            info['site'] = shorten_site(info['site_display'])
            # also grab specimen note for the jar letter/label
            notes = spec.get('note', [])
            if notes:
                info['label'] = notes[0].get('text', '')
            else:
                info['label'] = ''

    if 'label' not in info:
        info['label'] = ''

    return info

def shorten_performer(name):
    """Shorten common facility names for table display."""
    n = name.lower()
    if 'queens' in n and 'punchbowl' in n:
        return 'Queens Punchbowl'
    if 'adventist' in n and 'castle' in n:
        return 'Adventist Castle'
    return name[:20]

def shorten_site(display):
    """Shorten SNOMED body site display to a clinical abbreviation."""
    d = display.lower()
    if 'cecum' in d or 'caecum' in d:
        return 'Cecum'
    if 'ascending' in d:
        return 'Ascending'
    if 'hepatic' in d:
        return 'Hepatic flex.'
    if 'transverse' in d:
        return 'Transverse'
    if 'splenic' in d:
        return 'Splenic flex.'
    if 'descending' in d:
        return 'Descending'
    if 'sigmoid' in d:
        return 'Sigmoid'
    if 'rectum' in d or 'rectal' in d:
        return 'Rectum'
    if 'rectosigmoid' in d:
        return 'Rectosigmoid'
    # fallback: truncate
    return display[:15] if display else '?'


# ── Build per-colonoscopy summaries ────────────────────────────────────
colonoscopies = []

for dr in sorted(drs, key=lambda d: d.get('effectiveDateTime', d.get('issued', ''))):
    date = dr.get('effectiveDateTime', dr.get('issued', ''))[:10]

    # performer (Organization or Practitioner)
    performer_name = ''
    for perf in dr.get('performer', []):
        ref_str = perf.get('reference', '')
        display = perf.get('display', '')
        if display:
            performer_name = display
            break
        resolved = resolve_ref(ref_str)
        if resolved:
            performer_name = resolved.get('name', ref_str)
            break
    if not performer_name:
        performer_name = '-'

    # walk result references → Observations
    polyps = []
    for res_ref in dr.get('result', []):
        ref_str = res_ref.get('reference', '')
        obs = resolve_ref(ref_str)
        if obs and obs.get('resourceType') == 'Observation':
            polyps.append(extract_observation(obs))

    # compute summary stats
    n_polyps = len(polyps)
    n_adenomas = sum(1 for p in polyps if p['histo'] in ADENOMA_CODES)
    largest = max((p['size_mm'] or 0 for p in polyps), default=0)

    # flags
    flags = []
    piecemeal_list = [p for p in polyps if p.get('piecemeal')]
    if piecemeal_list:
        for pm in piecemeal_list:
            flags.append(f"PIECEMEAL {pm['size_mm']}mm {pm['site']}")
    hgd_count = sum(1 for p in polyps if p.get('dysplasia'))
    if hgd_count:
        flags.append(f"HGD x{hgd_count}")

    # histology tally
    histo_counts = defaultdict(int)
    for p in polyps:
        histo_counts[p['histo']] += 1
    histo_str = ', '.join(f"{v}{k}" for k, v in sorted(histo_counts.items(), key=lambda x: -x[1]))

    colonoscopies.append({
        'date': date,
        'performer': performer_name,
        'n_polyps': n_polyps,
        'n_adenomas': n_adenomas,
        'largest': largest,
        'flags': flags,
        'histo_str': histo_str,
        'polyps': polyps,
    })

# ── TIER 1: Summary table ─────────────────────────────────────────────
lines = []
lines.append('COLONOSCOPY SURVEILLANCE SUMMARY')
lines.append('=' * 95)
lines.append('')
lines.append('%-12s %-22s %6s %8s %8s  %s' % ('Date', 'Facility', 'Polyps', 'Adenoma', 'Largest', 'Histology'))
lines.append('-' * 95)

total_polyps = 0
total_adenomas = 0
for c in colonoscopies:
    perf_short = shorten_performer(c['performer'])
    largest_str = f"{int(c['largest'])}mm" if c['largest'] else '-'
    lines.append('%-12s %-22s %6d %8d %8s  %s' % (
        c['date'], perf_short, c['n_polyps'], c['n_adenomas'], largest_str, c['histo_str']))
    total_polyps += c['n_polyps']
    total_adenomas += c['n_adenomas']

lines.append('-' * 95)
lines.append('%-12s %-22s %6d %8d' % ('TOTAL', '', total_polyps, total_adenomas))

# ── High-risk features summary ─────────────────────────────────────────
lines.append('')
lines.append('HIGH-RISK FEATURES')
lines.append('-' * 50)
all_flags = []
for c in colonoscopies:
    for f in c['flags']:
        all_flags.append(f"{c['date']}: {f}")
if all_flags:
    for f in all_flags:
        lines.append(f"  ⚑ {f}")
else:
    lines.append('  None identified')

# lifetime advanced adenoma check
ever_large = any(p['size_mm'] and p['size_mm'] >= 10 and p['histo'] in ADENOMA_CODES
                 for c in colonoscopies for p in c['polyps'])
ever_villous = any(p['histo'] in ('VA', 'TVA')
                   for c in colonoscopies for p in c['polyps'])
ever_hgd = any(p.get('dysplasia') for c in colonoscopies for p in c['polyps'])
ever_piecemeal = any(p.get('piecemeal') for c in colonoscopies for p in c['polyps'])
ever_ssp = any(p['histo'] == 'SSP' for c in colonoscopies for p in c['polyps'])
max_adenoma_count = max((c['n_adenomas'] for c in colonoscopies), default=0)

lines.append('')
lines.append('USMSTF 2020 RISK FACTORS')
lines.append('-' * 50)
lines.append(f"  Adenoma ≥10mm:         {'YES' if ever_large else 'No'}")
lines.append(f"  Villous component:     {'YES' if ever_villous else 'No'}")
lines.append(f"  High-grade dysplasia:  {'YES' if ever_hgd else 'No'}")
lines.append(f"  Piecemeal excision:    {'YES' if ever_piecemeal else 'No'}")
lines.append(f"  Sessile serrated:      {'YES' if ever_ssp else 'No'}")
lines.append(f"  Max adenomas/exam:     {max_adenoma_count}")

# ── TIER 2: Per-colonoscopy polyp detail ───────────────────────────────
for c in colonoscopies:
    lines.append('')
    lines.append(f"{'─' * 95}")
    lines.append(f"COLONOSCOPY {c['date']}  —  {c['performer']}  —  {c['n_polyps']} polyps")
    lines.append(f"{'─' * 95}")
    if not c['polyps']:
        lines.append('  (no polyp data)')
        continue

    lines.append('  %-6s %-16s %-8s %6s  %-10s %-4s %s' % (
        'Label', 'Site', 'Histo', 'Size', 'Piecemeal', 'HGD', 'Malignancy'))
    lines.append('  ' + '-' * 75)
    for idx, p in enumerate(c['polyps']):
        raw_label = p.get('label', '') if p.get('label') else ''
        # jar-letter prefix pattern: "A. ..." or "B. ..."
        if len(raw_label) >= 2 and raw_label[0].isalpha() and raw_label[1] == '.':
            label = raw_label[:2]
        else:
            # descriptive label (e.g. 2022 "ASCENDING COLON..."): use index
            label = f"#{idx+1}"
        site = p['site'][:16] if p['site'] else '?'
        histo = p['histo']
        size_str = f"{int(p['size_mm'])}mm" if p['size_mm'] else '-'
        piecemeal = 'YES' if p.get('piecemeal') else ''
        hgd = 'YES' if p.get('dysplasia') else ''
        malig = 'clear' if p.get('malignancy') else '?'
        lines.append('  %-6s %-16s %-8s %6s  %-10s %-4s %s' % (
            label, site, histo, size_str, piecemeal, hgd, malig))

    # per-colonoscopy flag callouts
    if c['flags']:
        lines.append('')
        for f in c['flags']:
            lines.append(f"  ⚑ {f}")

result = '\n'.join(lines)
print(result)

with open(os.path.join(SCRIPT_DIR, 'colonoscopy-output.txt'), 'w') as f:
    f.write(result + '\n')
print('\nWritten to colonoscopy-output.txt')
