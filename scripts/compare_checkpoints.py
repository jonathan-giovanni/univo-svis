import os
import sys
import cv2
import numpy as np
from pathlib import Path
from dataclasses import dataclass

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from univo_svis.core.bootstrap import bootstrap
from univo_svis.detection.detector import DualModelDetector
from univo_svis.detection.roboflow_resolver import RoboflowResolver
from univo_svis.detection.image_analysis import run_static_analysis

@dataclass
class ComparisonMetric:
    persons: int
    with_vest: int
    without_vest: int
    raw_vests: int

def run_comparison():
    config = bootstrap()
    project_root = Path(__file__).parent.parent
    dataset_val = "/Users/admin/Documents/datasets/safety-vest-data-yolo-v1/valid/images"
    
    weights_best = project_root / "training_runs/safety_vest_yolo11_clean50_v1/weights/best.pt"
    weights_last = project_root / "training_runs/safety_vest_yolo11_clean50_v1/weights/last.pt"
    
    thresholds = [0.25, 0.30, 0.35]
    
    # Select a few representative images from validation set
    images = sorted([f for f in os.listdir(dataset_val) if f.endswith(('.png', '.jpg', '.jpeg'))])[:5]
    
    results = {}

    for name, weight_path in [("BEST", weights_best), ("LAST", weights_last)]:
        print(f"\n--- Testing Checkpoint: {name} ---")
        results[name] = {}
        
        # Override config weights for resolver
        config.vest_model.weights = str(weight_path.relative_to(project_root))
        
        resolver = RoboflowResolver(
            local_weights=config.vest_model.weights,
            workspace=config.roboflow.workspace,
            project=config.roboflow.project,
            version=config.roboflow.version,
            project_root=project_root,
        )
        detector = DualModelDetector(config, resolver)
        
        for thresh in thresholds:
            print(f"  Confidence Threshold: {thresh}")
            total_persons = 0
            total_with_vest = 0
            total_raw_vests = 0
            
            for img_name in images:
                img_path = os.path.join(dataset_val, img_name)
                frame = cv2.imread(img_path)
                if frame is None: continue
                
                # We override confidence in the call
                detector._config.vest_model.confidence_threshold = thresh
                analysis = run_static_analysis(frame, detector, 0.30)
                
                total_persons += analysis.total_persons
                total_with_vest += analysis.compliant_count
                total_raw_vests += len(analysis.vests)
            
            results[name][thresh] = ComparisonMetric(total_persons, total_with_vest, total_persons - total_with_vest, total_raw_vests)
            print(f"    Tally: Persons={total_persons}, WithVest={total_with_vest}, TotalRawVests={total_raw_vests}")

    # Final Summary Table
    print("\n\n" + "="*60)
    print("FINAL COMPARISON TABLE")
    print("="*60)
    print(f"{'Checkpt':<8} | {'Conf':<5} | {'Persons':<8} | {'WithVest':<8} | {'RawVests':<10}")
    print("-" * 60)
    for name in ["BEST", "LAST"]:
        for thresh in thresholds:
            m = results[name][thresh]
            print(f"{name:<8} | {thresh:<5} | {m.persons:<8} | {m.with_vest:<8} | {m.raw_vests:<10}")
    print("="*60)

if __name__ == "__main__":
    run_comparison()
