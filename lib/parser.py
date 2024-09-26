import xml.etree.ElementTree as ET
from collections import defaultdict
from pprint import pprint
import re

def etree_to_dict(t):
    tag = t.tag.split('}')[-1]
    d = {tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[tag]['#text'] = text
        else:
            d[tag] = text
    return d

def iter_field(obj, field):
    items = obj.get(field, [])
    if type(items) == dict:
        items = [items]
    return items

def get_namespace(element):
    m = re.match(r'\{(.*)\}', element.tag)
    return m.group(1) if m else ''

def parse_xml(xml_file):
    root = ET.fromstring(xml_file)
    root_dict = etree_to_dict(root)['ReportType']
    fields = []
    for section in iter_field(root_dict, 'sections'):
        for column in iter_field(section,'columns'):
            assert column['table'] == root_dict['baseObject']
            fields.append({
                'section': section['masterLabel'],
                'name': column['displayNameOverride'],
                'field': column['field'],
                'default': column['checkedByDefault'] == 'true',
            })
    root_dict.pop('sections')
    return {
        **root_dict,
        'namespace': get_namespace(root),
        'fields': fields,
    }

def dict_to_etree(d):
    def _to_etree(d, root):
        if d is None:
            pass
        elif isinstance(d, bool):
            root.text = str(d).lower()
        elif isinstance(d, str):
            root.text = d
        elif isinstance(d, dict):
            for k,v in d.items():
                assert isinstance(k, str)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, str)
                    root.text = v
                elif k.startswith('@'):
                    assert isinstance(v, str)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ET.SubElement(root, k))
                else:
                    _to_etree(v, ET.SubElement(root, k))
        else:
            raise TypeError('invalid type: ' + str(type(d)))
    assert isinstance(d, dict) and len(d) == 1
    tag, body = next(iter(d.items()))
    node = ET.Element(tag)
    _to_etree(body, node)
    ET.indent(node, space='    ', level=0)
    return ET.tostring(node, encoding='UTF-8', xml_declaration=True, short_empty_elements=False)

def unparse_xml(d):
    fields = d.pop('fields', [])
    sections = defaultdict(list)
    for field in fields:
        sections[field['section']].append({
            'checkedByDefault': field['default'],
            'displayNameOverride': field['name'],
            'field': field['field'],
            'table': d['baseObject'],
        })
    return dict_to_etree({'ReportType': {
        '@xmlns': d.pop('namespace','http://soap.sforce.com/2006/04/metadata'),
        **d,
        'sections': [
            {'columns': v, 'masterLabel': k}
            for k,v in sections.items()
        ],
    }})
    

if __name__ == '__main__':
    with open('/Users/ben/Documents/datajoin/hubspot-to-salesforce/force-app/main/default/reportTypes/Hubspot_Attributions.reportType-meta.xml', 'r') as f:
        file = f.read()
    parsed = parse_xml(file)
    pprint(parsed)
    unparsed = unparse_xml(parsed)
    # unparsed.write('./test.xml', encoding='utf-8', xml_declaration=True)
    print(unparsed.decode('utf-8'))
    print('hi')