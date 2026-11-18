"""Derive tasks from full exports; --check validates without writing."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

def load(p):
    return json.loads(p.read_text(encoding='utf-8'))

def indexed(kind, person):
    rows = load(DATA/'annotations'/person/f'{kind}_markup_{person}.json')
    result = {t['data']['sample_id']: t for t in rows}
    if len(result) != len(rows):
        raise ValueError(f'Duplicate IDs: {kind}/{person}')
    if kind == 'image' and any(type(s) is not int or s <= 0 for s in result):
        raise ValueError('Image sample_id must be a positive integer')
    return result

def prepare(check=False):
    for kind, folder, source in [('image','images','nikita'), ('review','reviews','egor')]:
        a, b = (indexed(kind,p) for p in ['nikita','egor'])
        if a.keys() != b.keys():
            raise ValueError(f'Different sample_id sets: {kind}')
        config = ET.parse(DATA/'tasks'/folder/'labeling_interface.xml').getroot()
        controls = {n.attrib['name']: n for n in config if 'name' in n.attrib}
        paths = set()
        for sid in a:
            left, right = a[sid]['data'], b[sid]['data']
            if kind == 'image':
                if left['image'] != right['image'] or left['image_sha256'] != right['image_sha256']:
                    raise ValueError(f'Different image identity: {sid}')
                file = (DATA/parse_qs(urlsplit(left['image']).query)['d'][0]).resolve()
                if not file.is_relative_to((DATA/'images').resolve()) or file in paths:
                    raise ValueError(f'Invalid or duplicate image path: {file}')
                paths.add(file)
                if hashlib.sha256(file.read_bytes()).hexdigest() != left['image_sha256']:
                    raise ValueError(f'Image checksum mismatch: {sid}')
            elif left['text'] != right['text'] or left['source_review_id'] != right['source_review_id']:
                raise ValueError(f'Different review identity: {sid}')
            for person, rows in [('nikita',a),('egor',b)]:
                if not rows[sid].get('annotations'):
                    raise ValueError(f'Missing annotation: {kind}/{person}/{sid}')
                for annotation in rows[sid]['annotations']:
                    for r in annotation.get('result', []):
                        if r['type'] == 'textarea':
                            if r['from_name'] not in ['source_url','author','license']:
                                raise ValueError(f'Unknown metadata field: {sid}')
                            continue
                        control = controls[r['from_name']]
                        if control.attrib.get('toName') != r['to_name']:
                            raise ValueError(f'Wrong control target: {sid}')
                        v = r['value']
                        allowed = {n.attrib['value'] for n in control}
                        if kind == 'image':
                            x,y,w,h = (v[k] for k in ['x','y','width','height'])
                            if not set(v['rectanglelabels']) <= allowed or min(x,y) < -1e-6 or min(w,h) <= 0 or max(x+w,y+h) > 100.000001:
                                raise ValueError(f'Invalid box: {person}/{sid}')
                        elif len(v['choices']) != 1 or not set(v['choices']) <= allowed:
                            raise ValueError(f'Invalid sentiment: {person}/{sid}')
        if kind == 'image':
            actual = {p.resolve() for p in (DATA/'images').rglob('*') if p.is_file()}
            if actual != paths:
                raise ValueError(f'Extra or missing images: {actual ^ paths}')
        rows = a if source == 'nikita' else b
        tasks = [{'data': rows[s]['data']} for s in sorted(rows)]
        output = DATA/'tasks'/folder/f'{kind}_tasks.json'
        if check:
            if load(output) != tasks:
                raise ValueError(f'Regenerate tasks: {output}')
        else:
            output.write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{kind}: {len(tasks)} shared samples; both exports valid; no answers in tasks')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    prepare(parser.parse_args().check)
