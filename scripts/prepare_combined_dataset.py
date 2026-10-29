"""Integra exportaciones locales sin modificar imagenes ni anotaciones originales."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import shutil
import time
import zipfile

from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[1]
NAME = 'agave_maleza_2026-10-21'
PATTERN = re.compile(r'_v(\d+)_h(\d+)_f(\d+)_t')


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate_labels(raw, source):
    lines = raw.decode('utf-8-sig').splitlines()
    boxes = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f'{source}:{number}: se esperaban 5 campos YOLO detect')
        values = [float(x) for x in fields]
        cls, x, y, w, h = values
        if not all(math.isfinite(v) for v in values) or cls != 0:
            raise ValueError(f'{source}:{number}: clase o numero invalido')
        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
            raise ValueError(f'{source}:{number}: coordenada fuera del intervalo normalizado')
        if min(x-w/2, y-h/2) < -0.00001 or max(x+w/2, y+h/2) > 1.00001:
            raise ValueError(f'{source}:{number}: caja fuera de la imagen')
        boxes.append(tuple(values))
    if len(boxes) != len(set(boxes)):
        raise ValueError(f'{source}: etiquetas duplicadas')
    return len(boxes)


def register_pixels(seen, pixel_hash, name, split, label_hash):
    """A reserve copy must never hide a previous active split for the same image."""
    prior = seen.get(pixel_hash)
    active = set() if split == 'reserve' else {split}
    if prior:
        active.update(prior['active_splits'])
        if len(active) > 1:
            raise ValueError(f"Imagen identica en splits distintos: {prior['image']} / {name}")
        if prior['label_hash'] != label_hash:
            raise ValueError('Imagen identica con etiquetas distintas')
        prior['active_splits'] = active
        return [prior['image'], name]
    seen[pixel_hash] = {'image':name,'active_splits':active,'label_hash':label_hash}
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--policy', type=Path, default=ROOT/'configs/datasets'/f'{NAME}.json')
    parser.add_argument('--extraction-manifest', type=Path)
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding='utf-8'))
    dest = ROOT/'datasets/prepared'/NAME
    stage = dest.with_name(dest.name+'.incomplete')
    if dest.exists() or stage.exists():
        raise SystemExit(f'La salida ya existe: {dest} o {stage}. No se sobrescribe.')
    old = ROOT/'datasets/yolo26'
    raw_dir = ROOT/'datasets/raw/maleza_2026-10-21'
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_zip = raw_dir/'agave_maleza.yolo26.zip'
    source_hash = digest_file(args.zip)
    if raw_zip.exists():
        if digest_file(raw_zip) != source_hash:
            raise ValueError('Ya existe un ZIP raw distinto')
    else:
        shutil.copy2(args.zip, raw_zip)
        if digest_file(raw_zip) != source_hash:
            raise ValueError('La copia del ZIP no coincide')
    (raw_dir/'procedencia.json').write_text(json.dumps({
        'source_download': str(args.zip.resolve()), 'sha256': source_hash,
        'bytes': raw_zip.stat().st_size, 'date': '2026-10-21',
        'note': 'Exportacion completa conservada sin modificaciones.'
    }, indent=2), encoding='utf-8')
    extraction = {}
    if args.extraction_manifest:
        for row in json.loads(args.extraction_manifest.read_text(encoding='utf-8')):
            extraction[(row['video_id'], row['frame_index'])] = row

    tasks = []
    for split in ('train', 'val', 'test'):
        for file in sorted((old/'images'/split).iterdir()):
            if file.suffix.lower() not in {'.jpg','.jpeg','.png'}:
                continue
            label = old/'labels'/split/(file.stem+'.txt')
            if not label.is_file():
                raise ValueError(f'Falta etiqueta: {label}')
            tasks.append(dict(source='historico_404', source_split=split, split=split,
                              image=file, label=label, name='historico__'+file.name,
                              video_id='', frame_index='', nominal_seconds='', reserve_reason=''))
    old_yaml = yaml.safe_load((old/'data.yaml').read_text(encoding='utf-8'))
    if old_yaml['nc'] != 1 or old_yaml['names'] != ['agave']:
        raise ValueError('Clases historicas inesperadas')
    if Counter(t['split'] for t in tasks) != Counter(train=295,val=73,test=36):
        raise ValueError('La particion historica debe conservar exactamente 295/73/36')

    with zipfile.ZipFile(raw_zip) as z:
        entries = defaultdict(list)
        for info in z.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in info.filename:
                raise ValueError('Ruta insegura dentro del ZIP')
            entries[info.filename].append(info)
        for name, members in entries.items():
            if len(members) > 1 and (name != 'data.yaml' or len({z.read(m) for m in members}) != 1):
                raise ValueError('Entrada ZIP duplicada no admitida: '+name)
        new_yaml = yaml.safe_load(z.read(entries['data.yaml'][0]))
        if new_yaml['nc'] != 1 or new_yaml['names'] != ['agave']:
            raise ValueError('La exportacion nueva no tiene la clase unica agave')
        for name in ('data.yaml', 'README.roboflow.txt', 'README.dataset.txt'):
            if name in entries:
                (raw_dir/name).write_bytes(z.read(entries[name][0]))
        for name in sorted(entries):
            p = PurePosixPath(name)
            if p.suffix.lower() not in {'.jpg','.jpeg','.png'}:
                continue
            if len(p.parts) != 3 or p.parts[1] != 'images':
                raise ValueError('Estructura inesperada: '+name)
            label = str(p.parent.parent/'labels'/(p.stem+'.txt'))
            if label not in entries:
                raise ValueError('Falta etiqueta: '+label)
            match = PATTERN.search(p.name)
            if not match:
                raise ValueError('No se puede recuperar video/frame: '+name)
            video = 'v'+match[1]
            frame = int(match[3])
            seconds = frame / policy['fps_for_nominal_time']
            split = policy['video_splits'][video]
            reason = ''
            for interval in policy.get('reserve_ranges_seconds', {}).get(video, []):
                lower, upper = interval
                if seconds >= lower and (upper is None or seconds < upper):
                    split, reason = 'reserve', 'guarda_temporal_60s'
            tasks.append(dict(source='maleza_1826', source_split=p.parts[0], split=split,
                              image=name, label=label, name=f'maleza__{video}_f{frame:05d}'+p.suffix.lower(),
                              video_id=video, frame_index=frame, nominal_seconds=seconds,
                              reserve_reason=reason))
        if sum(t['source']=='historico_404' for t in tasks) != 404 or sum(t['source']=='maleza_1826' for t in tasks) != 1826:
            raise ValueError('El numero de imagenes no corresponde a esta version (404 + 1826)')
        expected_labels = {t['label'] for t in tasks if t['source']=='maleza_1826'}
        actual_labels = {n for n in entries if '/labels/' in n and n.endswith('.txt')}
        if actual_labels != expected_labels:
            raise ValueError('Etiquetas huerfanas en ZIP')
        stage.mkdir(parents=True)
        for split in ('train','val','test','reserve'):
            (stage/'images'/split).mkdir(parents=True)
            (stage/'labels'/split).mkdir(parents=True)
        rows, files_seen, pixels_seen, names_seen = [], {}, {}, set()
        duplicate_groups = []
        started = time.monotonic()
        for index, task in enumerate(tasks, 1):
            new = task['source']=='maleza_1826'
            encoded = z.read(task['image']) if new else task['image'].read_bytes()
            labels = z.read(task['label']) if new else task['label'].read_bytes()
            file_hash = hashlib.sha256(encoded).hexdigest()
            with Image.open(io.BytesIO(encoded)) as im:
                im.load()
                width, height = im.size
                rgb = im.convert('RGB')
                pixel_hash = hashlib.sha256(f'{width}x{height}:'.encode()+rgb.tobytes()).hexdigest()
            boxes = validate_labels(labels, task['label'])
            if task['name'] in names_seen:
                raise ValueError('Nombre de salida duplicado: '+task['name'])
            names_seen.add(task['name'])
            duplicate = register_pixels(pixels_seen, pixel_hash, task['name'], task['split'], hashlib.sha256(labels).hexdigest())
            if duplicate:
                duplicate_groups.append(duplicate)
            files_seen[file_hash] = task['name']
            image_rel = f"images/{task['split']}/{task['name']}"
            label_rel = f"labels/{task['split']}/{Path(task['name']).stem}.txt"
            (stage/image_rel).write_bytes(encoded)
            (stage/label_rel).write_bytes(labels)
            original = extraction.get((task['video_id'],task['frame_index']), {})
            if new and extraction and not original:
                raise ValueError('Fotograma nuevo no encontrado en manifiesto de extraccion')
            rows.append(dict(source=task['source'], source_split=task['source_split'], split=task['split'],
                             source_image=str(task['image']), source_label=str(task['label']),
                             image=image_rel, label=label_rel, video_id=task['video_id'],
                             frame_index=task['frame_index'], nominal_seconds=task['nominal_seconds'],
                             video_source=original.get('source_relative',''), original_extracted_image=original.get('relative_image',''),
                             reserve_reason=task['reserve_reason'], width=width,height=height,boxes=boxes,
                             sha256=file_hash,pixel_sha256=pixel_hash,label_sha256=hashlib.sha256(labels).hexdigest()))
            if index % 100 == 0:
                print(f'Validadas y copiadas {index}/{len(tasks)} imagenes ({time.monotonic()-started:.0f}s)',flush=True)

    with (stage/'manifest.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (stage/'split_policy.json').write_text(json.dumps(policy,indent=2,ensure_ascii=False),encoding='utf-8')
    data = {'path':dest.as_posix(), 'train':'images/train','val':'images/val','test':'images/test','nc':1,'names':['agave']}
    (stage/'data.yaml').write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding='utf-8')
    stats = {split:{'images':sum(r['split']==split for r in rows),
                    'boxes':sum(r['boxes'] for r in rows if r['split']==split),
                    'empty_labels':sum(r['boxes']==0 for r in rows if r['split']==split),
                    'by_source':dict(Counter(r['source'] for r in rows if r['split']==split))}
             for split in ('train','val','test','reserve')}
    summary = {'version':NAME,'total_images_preserved':len(rows),'active_images':sum(stats[s]['images'] for s in ('train','val','test')),
               'total_boxes':sum(r['boxes'] for r in rows),'splits':stats,
               'dimensions':dict(Counter(f"{r['width']}x{r['height']}" for r in rows)),
               'exact_pixel_duplicate_groups':duplicate_groups,'source_zip_sha256':source_hash,
               'source_zip_duplicate_data_yaml_entries':len(entries['data.yaml']),
               'limitations':policy['limitations'], 'validation':'All images decoded; labels checked; originals copied byte-for-byte; no resize/augmentation.'}
    (stage/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    (stage/'README.md').write_text('# Dataset combinado de agave\n\n'
        '404 imagenes historicas y 1826 nuevas de maleza. Una clase: `agave`.\n\n'
        '`data.yaml` es la entrada para Ultralytics; `manifest.csv` conserva procedencia, hashes, cajas y split. '
        '`summary.json` contiene los conteos verificados y `split_policy.json` la regla reproducible.\n\n'
        '`images/reserve` y sus etiquetas conservan las guardas temporales de 60 s; no aparecen en data.yaml. '
        'No se modificaron ni redimensionaron las imagenes o cajas.\n\n'
        'La evaluacion nueva es interna a la misma salida de campo; no prueba generalizacion a otro campo. '
        'La particion historica se conserva para trazabilidad, con su posible correlacion temporal original.\n',encoding='utf-8')
    stage.rename(dest)
    print(json.dumps(summary,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    main()
