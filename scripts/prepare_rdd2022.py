#!/usr/bin/env python3
"""Download RDD2022 India and convert its Pascal-VOC labels to one-class YOLO.

The official RDD2022 archive contains road images and XML annotations. This
script keeps only class D40 (pothole), creates train/val splits, and writes a
YOLO dataset.yaml file.
"""
from pathlib import Path
import argparse, random, shutil, urllib.request, zipfile, xml.etree.ElementTree as ET
from PIL import Image

URL = "https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/Country_Specific_Data_CRDDC2022/RDD2022_India.zip"


def download(url, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        print(f"Downloading {url} -> {target}")
        urllib.request.urlretrieve(url, target)
    else:
        print(f"Using existing archive: {target}")


def find_pairs(root):
    pairs = []
    for xml_path in root.rglob("*.xml"):
        image_path = next((p for p in [xml_path.with_suffix('.jpg'), xml_path.with_suffix('.JPG'),
                                       xml_path.parent / (xml_path.stem + '.png')] if p.exists()), None)
        if image_path:
            pairs.append((image_path, xml_path))
    return pairs


def convert(xml_path):
    root = ET.parse(xml_path).getroot()
    size = root.find("size")
    w, h = float(size.findtext("width")), float(size.findtext("height"))
    labels = []
    for obj in root.findall("object"):
        if obj.findtext("name", "").strip().upper() != "D40":
            continue
        box = obj.find("bndbox")
        xmin = max(0.0, float(box.findtext("xmin")))
        ymin = max(0.0, float(box.findtext("ymin")))
        xmax = min(w, float(box.findtext("xmax")))
        ymax = min(h, float(box.findtext("ymax")))
        if xmax <= xmin or ymax <= ymin:
            continue
        xc, yc = (xmin + xmax) / 2 / w, (ymin + ymax) / 2 / h
        bw, bh = (xmax - xmin) / w, (ymax - ymin) / h
        labels.append(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='data', help='Project data directory')
    ap.add_argument('--val-ratio', type=float, default=0.2)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()
    root = Path(args.root)
    archive = root / 'raw' / 'RDD2022_India.zip'
    extracted = root / 'raw' / 'RDD2022_India'
    out = root / 'processed' / 'rdd2022_pothole'
    download(URL, archive)
    if not extracted.exists():
        extracted.mkdir(parents=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(extracted)
    pairs = find_pairs(extracted)
    random.Random(args.seed).shuffle(pairs)
    split = int(len(pairs) * (1 - args.val_ratio))
    train, val = pairs[:split], pairs[split:]
    for name, items in [('train', train), ('val', val)]:
        (out / 'images' / name).mkdir(parents=True, exist_ok=True)
        (out / 'labels' / name).mkdir(parents=True, exist_ok=True)
        kept = 0
        for image, xml in items:
            labels = convert(xml)
            # Negative images are useful, but RDD2022's train set is mainly annotated damage.
            dst_img = out / 'images' / name / image.name
            shutil.copy2(image, dst_img)
            (out / 'labels' / name / f'{image.stem}.txt').write_text('\n'.join(labels) + ('\n' if labels else ''))
            kept += bool(labels)
        print(f'{name}: {len(items)} images, {kept} images containing potholes')
    yaml = out / 'dataset.yaml'
    yaml.write_text(f"path: {out.resolve()}\ntrain: images/train\nval: images/val\nnc: 1\nnames: [pothole]\n")
    print(f'Wrote {yaml}')
    print('Next: open notebooks/AI_Potholes_Detection.ipynb and run all cells.')

if __name__ == '__main__':
    main()
