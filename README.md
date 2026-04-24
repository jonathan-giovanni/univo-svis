# UNIVO-SVIS

**University of Oviedo — Safety Vest Inspection Suite**

## What the app does
This is a professional computer vision application designed to enforce safety compliance. It detects persons and safety vests in images and real-time video streams, automatically determining who is not wearing a vest based on a spatial overlap analysis. It tracks compliance totals, supports visual inspection modes, and allows for evidence capture and recording.

## Requirements
- Python 3.12+
- A standard Python Virtual Environment (`venv`)
- Core dependencies: `PySide6`, `ultralytics`, `opencv-python`
- *(Optional)* A Roboflow API key configured as `ROBOFLOW_API_KEY` in your environment (if relying on the Roboflow Serverless model instead of local weights)

## ⚡ Plug-and-Play Setup
The application comes **Hot Ready / Plug-and-Play**. Both the Person detector (`yolo11n.pt`) and the custom Safety Vest detector (`best.pt`) are **pre-bundled securely** in the repository. You do not need to download or place any model files manually!

1. **Clone the repository and enter the directory**:
   ```bash
   git clone https://github.com/jonathan-giovanni/univo-svis.git
   cd univo-svis
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up Serverless Fallback (Optional)**:
   If you wish to use the Roboflow Serverless mode, set your key:
   ```bash
   export ROBOFLOW_API_KEY="your_api_key_here"
   ```

## How to run the app
Start the application by running the provided dev script:
```bash
python scripts/run_dev.py
```
*(Alternatively: `PYTHONPATH=src python -m univo_svis.main`)*

## How to use the app
1. **Choose your Vest Model Source** in the top navigation panel:
   - **Local Model**: Uses your provided `best.pt` local weights.
   - **Roboflow Serverless**: Connects securely to the Cloud-hosted serverless inference engine via `inference-sdk`.
2. Select **Image Analysis** or **Live Monitor** from the Home screen.
3. Once in the workspace, use the **File** menu to **Open Image**, **Open Video**, or **Open Webcam**.
4. Adjust the confidence and threshold sliders if necessary.
5. In Image mode: Click **Process** to trigger detection and see the detailed analysis.
6. In Live mode: Read the real-time compliance tallies directly from the console. You can **Pause**, **Record**, and **Capture** streams interactively.

## Final Model Source Explanation
This application strictly adheres to a robust Dual-Model paradigm. It pairs a foundational Ultralytics YOLOv11 person detector (`yolo11n.pt`) alongside a specialized Safety Vest detector. 

For the vest detector, you can dynamically toggle between two sources in the UI:
- **Local Model**: A student-trained YOLOv11 checkpoint directly integrated via local inference (highly recommended for performance). 
- **Roboflow Serverless Mode**: Remote serverless inference via `inference-sdk` tied to the exact underlying dataset project (`safety-vest-data-yolo`, version `1`).
