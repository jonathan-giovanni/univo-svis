# UNIVO-SVIS

**University of Oviedo — Safety Vest Inspection Suite**

A professional desktop computer vision application that detects persons and safety vests in images and video streams, determining compliance using bounding box overlap analysis.

## Model Architecture

| Model | Purpose | Source |
|-------|---------|--------|
| `yolo11n.pt` | Person detection | Ultralytics pretrained (COCO) |
| `best.pt` | Safety vest detection | Custom Roboflow-trained ([safety-vest-data-yolo](https://app.roboflow.com/jonathans-workspace-zetah/safety-vest-data-yolo/1)) |

## Quick Start

### Prerequisites

- Python 3.12+
- macOS / Linux / Windows

### Setup

```bash
# Clone the repository
git clone https://github.com/jonathan-giovanni/univo-svis.git
cd univo-svis

# Create virtual environment and install dependencies
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (Optional) Install Roboflow fallback support
pip install roboflow
```

### Configuration

Edit `config/app.yaml` to adjust:
- Model paths and confidence thresholds
- Overlap threshold for vest detection fusion
- Video capture settings
- Output directories

### Model Setup

1. **Person model**: Place `yolo11n.pt` in `models/yolo/` (auto-downloads on first run)
2. **Vest model**: Place your trained `best.pt` in `models/custom/`
   - Fallback: Set `ROBOFLOW_API_KEY` environment variable for hosted inference

### Running

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the application
PYTHONPATH=src python -m univo_svis.main

# Or use the dev launcher
python scripts/run_dev.py
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run smoke test
python scripts/smoke_test.py
```

## Project Structure

```
univo-svis/
├── config/          # Application configuration (YAML)
├── src/univo_svis/  # Source code
│   ├── presentation/    # UI layer (PySide6)
│   ├── application/     # Service/orchestration layer
│   ├── domain/          # Business logic and entities
│   └── infrastructure/  # YOLO, OpenCV, config, logging
├── tests/           # Unit and integration tests
├── models/          # YOLO model weights (.gitignored)
├── output/          # Captures, recordings, logs
├── scripts/         # Dev utilities
└── docs/            # Documentation
```

## Tech Stack

- **Python 3.12** — Language
- **PySide6** — Desktop GUI framework
- **Ultralytics YOLO** — Object detection
- **OpenCV** — Image/video processing
- **PyYAML** — Configuration

## License

GPL-3.0-or-later
