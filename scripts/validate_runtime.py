import os
import sys
import cv2
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from univo_svis.core.bootstrap import bootstrap
from univo_svis.detection.roboflow_resolver import RoboflowResolver
from univo_svis.detection.detector import DualModelDetector
from univo_svis.detection.image_analysis import run_static_analysis

def validate_runtime():
    print("--- REAL PROJECT RUNTIME VALIDATION ---")
    config = bootstrap()
    project_root = Path(__file__).parent.parent
    resolver = RoboflowResolver(
        local_weights=config.vest_model.weights,
        workspace=config.roboflow.workspace,
        project=config.roboflow.project,
        version=config.roboflow.version,
        project_root=project_root,
        api_key_env=config.roboflow.api_key_env
    )
    detector = DualModelDetector(config, resolver)
    
    # Test images from validation set
    test_img_path = "/Users/admin/Documents/datasets/safety-vest-data-yolo-v1/valid/images/003_png.rf.dYdRY0KeeLUEG3VRM8qI.png"
    if not os.path.exists(test_img_path):
        print(f"Error: Test image not found at {test_img_path}")
        return

    frame = cv2.imread(test_img_path)
    if frame is None:
        print("Error: Could not read frame")
        return
        
    print(f"\nProcessing Image: {test_img_path}")
    result = run_static_analysis(frame, detector, config.fusion.overlap_threshold)
    
    print("\n[DETECTION SUMMARY]")
    print(f"  Total Persons: {result.total_persons}")
    print(f"  With Vest   : {result.compliant_count}")
    print(f"  Without Vest: {result.non_compliant_count}")
    
    # Check if we got any detections
    if result.total_persons > 0:
        print("\n✓ SUCCESS: Detected persons in real application logic.")
    else:
        print("\n✖ WARNING: No persons detected. Check image contents.")
        
    if result.compliant_count > 0:
        print("✓ SUCCESS: Detected vests in real application logic.")
    else:
        # Check raw vest detections to see if they just didn't match the person
        if len(result.vests) > 0:
             print(f"✓ INFO: Detected {len(result.vests)} raw vests, but 0 compliance matches (IOA check).")
        else:
             print("✓ INFO: No vests detected (expected if people have no vests).")

    print(f"\n[CONSOLE OUTPUT COMPLIANCE]")
    print(f"PERSONS_TOTAL: {result.total_persons}")
    print(f"PERSONS_WITH_VEST: {result.compliant_count}")
    print(f"PERSONS_WITHOUT_VEST: {result.non_compliant_count}")

    print("\n--- VALIDATION COMPLETE ---")

if __name__ == "__main__":
    validate_runtime()
