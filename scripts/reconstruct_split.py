import os
import random
import shutil
from pathlib import Path

def reconstruct_split():
    dataset_root = Path("/Users/admin/Downloads/Safety Vest Data YOLO.yolov11")
    src_images = dataset_root / "train" / "images"
    src_labels = dataset_root / "train" / "labels"
    
    # Target structure
    splits = {
        "train": 213,
        "valid": 29,
        "test": 24
    }
    
    print(f"--- Dataset Audit (Initial) ---")
    all_images = sorted(list(src_images.glob("*")))
    # Filter for standard image extensions
    all_images = [f for f in all_images if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    
    print(f"Total images found: {len(all_images)}")
    
    # Verification: check for labels
    valid_pairs = []
    for img_path in all_images:
        label_path = src_labels / (img_path.stem + ".txt")
        if label_path.exists():
            valid_pairs.append((img_path, label_path))
    
    print(f"Matched image/label pairs: {len(valid_pairs)}")
    
    if len(valid_pairs) != 266:
        print(f"WARNING: Expected 266 pairs, found {len(valid_pairs)}")
        
    # Shuffle
    random.seed(42)
    random.shuffle(valid_pairs)
    
    # Prepare directories
    for split in splits:
        (dataset_root / split / "images").mkdir(parents=True, exist_ok=True)
        (dataset_root / split / "labels").mkdir(parents=True, exist_ok=True)
        
    # Distribution
    current_idx = 0
    for split, count in splits.items():
        pairs = valid_pairs[current_idx : current_idx + count]
        current_idx += count
        
        print(f"Moving {len(pairs)} pairs to {split}...")
        for img, lbl in pairs:
            # We move them if they aren't already there
            dest_img = dataset_root / split / "images" / img.name
            dest_lbl = dataset_root / split / "labels" / lbl.name
            
            if img != dest_img:
                shutil.move(str(img), str(dest_img))
            if lbl != dest_lbl:
                shutil.move(str(lbl), str(dest_lbl))
                
    # Final counts verification
    print(f"\n--- Final Counts ---")
    for split in splits:
        img_count = len(list((dataset_root / split / "images").glob("*")))
        lbl_count = len(list((dataset_root / split / "labels").glob("*")))
        print(f"{split}/images: {img_count}")
        print(f"{split}/labels: {lbl_count}")

    # Update data.yaml
    data_yaml_path = dataset_root / "data.yaml"
    with open(data_yaml_path, "w") as f:
        f.write(f"train: {dataset_root}/train/images\n")
        f.write(f"val: {dataset_root}/valid/images\n")
        f.write(f"test: {dataset_root}/test/images\n\n")
        f.write("nc: 1\n")
        f.write("names: ['safety_vest']\n")
    
    print(f"\nUpdated {data_yaml_path} with absolute paths.")

if __name__ == "__main__":
    reconstruct_split()
