This folder includes a small, usable demonstration dataset under `sample/` so the GitHub repository contains actual project data rather than documentation only.

```text
sample/
├── dataset.yaml
├── images/
│   ├── pothole_01.jpg
│   └── pothole_02.jpg
└── labels/
    ├── pothole_01.txt
    └── pothole_02.txt
```

The labels use YOLO object-detection format: `class_id center_x center_y width height`. The only class is `0 = pothole`. The sample is for demonstrating the data format and testing the workflow; it is not a statistically valid benchmark and must not be used to claim model accuracy.

For the full reproducible training workflow, run this from the repository root:

```bash
python scripts/prepare_rdd2022.py --root data
```

The script downloads the official RDD2022 India archive into `data/raw/`, extracts it, keeps pothole class `D40`, converts Pascal VOC XML annotations into YOLO labels, and writes the processed dataset under `data/processed/rdd2022_pothole/`. The full archive is intentionally not committed to GitHub because it may be large and its redistribution terms must be reviewed.

Sources: RDD2022 project at https://github.com/sekilab/RoadDamageDetector and the RDD2022 dataset record at https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547. Review source terms before public redistribution.
