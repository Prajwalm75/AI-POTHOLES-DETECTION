from pathlib import Path
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(text): cells.append(nbf.v4.new_code_cell(text))

md("""# AI Potholes Detection

This notebook trains a one-class YOLO object detector for **visible potholes**. It is designed for Linux JupyterLab and uses the official RDD2022 India road-damage archive. The companion script converts the archive's Pascal VOC XML annotations into YOLO format and keeps class `D40` (pothole).

Run the cells in order. For a quick CPU experiment use 10 epochs; for a stronger run use 30–50 epochs and a GPU if available.""")

md("## 1. Install dependencies\n\nRun this once in a terminal from the project root, then restart the kernel if Jupyter was already open:\n\n```bash\npip install -r requirements.txt\n```\n\nThe cells below assume the notebook is inside the project folder.")
code("""from pathlib import Path
import os, sys, random, shutil, subprocess, yaml

PROJECT = Path.cwd()
if PROJECT.name == 'notebooks':
    PROJECT = PROJECT.parent
DATA_ROOT = PROJECT / 'data'
PROCESSED = DATA_ROOT / 'processed' / 'rdd2022_pothole'
RUNS = PROJECT / 'runs'
print('Project:', PROJECT)
print('Python:', sys.version)
""")

md("## 2. Prepare the real dataset\n\nThis runs the included downloader/converter. It downloads the official RDD2022 India archive, extracts it, finds XML/image pairs, retains only the D40 pothole objects, creates an 80/20 split, and writes `dataset.yaml`. The archive is several hundred MB, so the first run may take time.")
code("""# Run once. If the dataset is already prepared, this is safe to run again.
script = PROJECT / 'scripts' / 'prepare_rdd2022.py'
subprocess.run([sys.executable, str(script), '--root', str(DATA_ROOT), '--val-ratio', '0.2', '--seed', '42'], check=True)
DATA_YAML = PROCESSED / 'dataset.yaml'
print(DATA_YAML)
print(DATA_YAML.read_text())
""")

md("## 3. Inspect the class distribution and sample labels")
code("""from collections import Counter
from PIL import Image
import matplotlib.pyplot as plt

for split in ['train', 'val']:
    label_dir = PROCESSED / 'labels' / split
    image_dir = PROCESSED / 'images' / split
    labels = list(label_dir.glob('*.txt'))
    boxes = sum(len(p.read_text().strip().splitlines()) for p in labels if p.read_text().strip())
    positives = sum(bool(p.read_text().strip()) for p in labels)
    print(f'{split}: {len(list(image_dir.glob("*")))} images, {positives} positive images, {boxes} pothole boxes')

sample_images = list((PROCESSED / 'images' / 'train').glob('*'))[:12]
fig, axes = plt.subplots(3, 4, figsize=(16, 10))
for ax, path in zip(axes.ravel(), sample_images):
    ax.imshow(Image.open(path))
    ax.set_title(path.name, fontsize=8)
    ax.axis('off')
plt.tight_layout()
""")

md("## 4. Load a pretrained detector")
code("""import torch
from ultralytics import YOLO

DEVICE = 0 if torch.cuda.is_available() else 'cpu'
print('Device:', 'CUDA GPU' if DEVICE == 0 else 'CPU')
# Transfer learning from a small pretrained model is fast and practical for a prototype.
model = YOLO('yolo11n.pt')
""")

md("## 5. Train\n\nThe best checkpoint is saved under `runs/pothole_yolo/weights/best.pt`. Increase `EPOCHS` for a final experiment. `patience` stops early if validation stops improving.")
code("""EPOCHS = 30
IMG_SIZE = 640
BATCH = 16 if DEVICE == 0 else 4

train_results = model.train(
    data=str(DATA_YAML),
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=BATCH,
    device=DEVICE,
    project=str(RUNS),
    name='pothole_yolo',
    pretrained=True,
    patience=10,
    seed=42,
    workers=2,
    plots=True,
)
BEST = RUNS / 'pothole_yolo' / 'weights' / 'best.pt'
print('Best checkpoint:', BEST)
""")

md("## 6. Validate and record metrics")
code("""best_model = YOLO(str(BEST))
metrics = best_model.val(data=str(DATA_YAML), imgsz=IMG_SIZE, device=DEVICE, plots=True)
print(f'mAP50: {metrics.box.map50:.4f}')
print(f'mAP50-95: {metrics.box.map:.4f}')
print('Per-class precision:', metrics.box.p)
print('Per-class recall:', metrics.box.r)
""")

md("## 7. Predict on a validation image")
code("""val_images = list((PROCESSED / 'images' / 'val').glob('*'))
assert val_images, 'No validation images found. Run dataset preparation first.'
result_list = best_model.predict(source=str(val_images[0]), conf=0.25, iou=0.5, save=True, project=str(RUNS), name='predict', device=DEVICE)
annotated = result_list[0].plot()
plt.figure(figsize=(12, 8))
plt.imshow(annotated[..., ::-1])
plt.axis('off')
plt.title('Pothole detection')
plt.show()
print('Saved annotated output under:', RUNS / 'predict')
""")

md("## 8. Batch inference on a folder")
code("""# Change INPUT_PATH to a local image, a folder, or a video file.
INPUT_PATH = str(PROCESSED / 'images' / 'val')
batch_results = best_model.predict(source=INPUT_PATH, conf=0.25, save=True, save_txt=True,
                                   project=str(RUNS), name='batch_predictions', device=DEVICE)
print('Batch inference complete. Review:', RUNS / 'batch_predictions')
""")

md("## 9. Optional video or webcam inference\n\nUse a local video path for reproducible inference. For a webcam, set `SOURCE = 0` and run on a machine with camera access. Press `q` in the display window to stop.")
code("""# Example: SOURCE = '/absolute/path/to/road_video.mp4'
# SOURCE = 0
# best_model.predict(source=SOURCE, conf=0.30, show=True, save=True, project=str(RUNS), name='video_predictions', device=DEVICE)
""")

md("## 10. Export for deployment\n\nONNX can be useful for integrating the detector into another Linux service. Review the Ultralytics license and your target runtime before deployment.")
code("""# Uncomment when needed:
# exported = best_model.export(format='onnx', imgsz=IMG_SIZE)
# print(exported)
""")

md("## 11. Report interpretation and next steps\n\nUse mAP50, mAP50-95, precision, recall, and false positives on a local held-out sample. A high score on a public dataset does not guarantee performance on another city, camera, season, or lighting condition. Before operational use, add representative local images, check for data leakage, tune the confidence threshold, and have road inspectors review predictions. The model detects visible potholes; it does not infer depth, repair cost, or legal responsibility.")

nb['cells'] = cells
nb['metadata'] = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python', 'version': '3.10'}}
out = Path('/home/ubuntu/AI_Potholes_Detection/notebooks/AI_Potholes_Detection.ipynb')
out.write_text(nbf.writes(nb), encoding='utf-8')
print(out)
