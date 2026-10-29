from pathlib import Path
import argparse
import re,json
from datetime import datetime, timezone
from _common import DOCUMENTS, TEMP

parser = argparse.ArgumentParser(description='Revisa el orden de las referencias del capítulo 2 ampliado.')
parser.add_argument('--apply', action='store_true', help='Aplica el orden al Markdown actual y conserva una copia previa local.')
options = parser.parse_args()
p=DOCUMENTS/'Capitulo_2_Marco_teorico_ampliado.md'
text=p.read_text(encoding='utf-8')
body,refs=text.split('# Referencias del capítulo',1)
entries={int(m.group(1)):m.group(2) for m in re.finditer(r'^\[(\d+)\] (.*?)(?=\n\n\[\d+\]|\Z)',refs.strip(),re.M|re.S)}
order=[]
for m in re.finditer(r'\[(\d+(?:,\s*\d+)*)\]',body):
    for n in map(int,re.findall(r'\d+',m.group(1))):
        if n not in order:order.append(n)
assert set(entries)==set(order), (set(entries)-set(order),set(order)-set(entries))
mapping={n:i+1 for i,n in enumerate(order)}
def swap(m):return '['+', '.join(str(mapping[int(n)]) for n in re.findall(r'\d+',m.group(1)))+']'
body=re.sub(r'\[(\d+(?:,\s*\d+)*)\]',swap,body)
ordered='\n\n'.join(f'[{mapping[n]}] {entries[n].strip()}' for n in order)
updated = body+'# Referencias del capítulo\n\n'+ordered+'\n'
print('References ordered by first appearance:',len(order))
print(json.dumps(mapping, indent=2))
if options.apply:
    TEMP.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = TEMP / f'Capitulo_2_antes_de_ordenar_{stamp}.md'
    backup.write_bytes(p.read_bytes())
    p.write_text(updated, encoding='utf-8')
    (TEMP/'orden_referencias_ampliado.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
    print(f'Markdown actualizado. Copia previa local: {backup}')
else:
    print('Solo revisión; ningún archivo modificado. Usa --apply para actualizar el Markdown.')
