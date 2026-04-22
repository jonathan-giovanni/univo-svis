# UNIVO-SVIS

**University of Oviedo — Safety Vest Inspection Suite**

A professional desktop computer vision application that detects persons and safety vests in images and video streams, determining compliance using bounding box overlap analysis.

## Model Architecture

| Model | Purpose | Source |
|-------|---------|--------|
| `yolo11n.pt` | Person detection | Ultralytics pretrained (COCO) |
| `best.pt` | Safety vest detection | Custom Roboflow-trained ([safety-vest-data-yolo](https://app.roboflow.com/jonathans-workspace-zetah/safety-vest-data-yolo/1)) |

**Overlap Rule**: `overlap = intersection_area(person_box, vest_box) / vest_box_area`. Default: `0.30`.

## Quick Start

### Setup

```bash
# Clone and enter repo
git clone https://github.com/jonathan-giovanni/univo-svis.git
cd univo-svis

# Create virtual environment and install dependencies
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running

```bash
# Standard run
PYTHONPATH=src python -m univo_svis.main

# Fast dev run (MacOS)
python scripts/run_dev.py
```

## Keyboard Shortcuts (Live Monitor)

| Key | Action |
|-----|--------|
| `O` / `V` | Open Image or Video File |
| `W` | Open Webcam |
| `Space` | Pause / Resume monitoring |
| `C` | Capture single annotated frame |
| `R` | Start / Stop Video Recording |
| `H` | Toggle Help Overlay |
| `Esc` / `Q` | Stop monitoring / Leave mode |

## Project Structure

```
univo-svis/
├── src/univo_svis/
│   ├── core/           # Configuration, i18n, logging, bootstrap
│   ├── detection/      # YOLO detector, fusion, annotator, video worker
│   └── ui/             # PySide6 views and custom widgets
├── tests/              # Unit and integration tests
├── models/             # YOLO weights (yolo11n.pt, best.pt)
├── output/             # Captures, recordings, logs
├── scripts/            # Dev utilities (verify.sh, run_dev.py)
└── config/             # YAML configuration
```

## Tech Stack

- **Python 3.12** — Modern type-hinted core
- **PySide6 (Qt)** — Premium responsive GUI
- **Ultralytics YOLO11** — State-of-the-art object detection
- **OpenCV** — Professional media processing

## License

GPL-3.0-or-later
