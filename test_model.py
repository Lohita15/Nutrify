import os
import sys
import time
import json
import argparse
import cv2
import traceback
from pathlib import Path

# Fix relative imports by appending the backend path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

try:
    from backend.nutrify_utils.model_loader import ModelLoader, InferenceEngine
except ImportError as e:
    print(f"❌ Error importing backend modules. Ensure you're running this from the project root. Detail: {e}")
    sys.exit(1)

def setup_directories():
    """Create necessary directories if they do not exist."""
    test_images_dir = os.path.join(PROJECT_ROOT, "test_images")
    outputs_dir = os.path.join(PROJECT_ROOT, "outputs")
    
    os.makedirs(test_images_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    return test_images_dir, outputs_dir

def initialize_models():
    """Test Model Loading Check"""
    print("\n" + "="*60)
    print("🧠 STATING MODEL LOADING TEST")
    print("="*60)
    
    start_time = time.time()
    try:
        model_loader = ModelLoader(model_dir=os.path.join(BACKEND_DIR, "model"))
        yolo_model, classifier_model = model_loader.load_all_models()
        load_time = time.time() - start_time
        
        print("\n--- Model Loading Summary ---")
        if yolo_model:
            print("✓ YOLO model loaded successfully")
        else:
            print("❌ YOLO model failed to load")
            
        if classifier_model:
            print("✓ Classifier loaded successfully")
        else:
            print("❌ Classifier model failed to load")
        
        print(f"⌚ Total Loading Time: {load_time * 1000:.2f} ms")
        
        if not yolo_model:
            return None
        
        inference_engine = InferenceEngine(yolo_model, classifier_model, device=model_loader.device)
        return inference_engine
    except Exception as e:
        print(f"❌ Critical error during model loading: {e}")
        traceback.print_exc()
        return None

def process_single_image(inference_engine, image_path, outputs_dir, save_images=False):
    """Run inference on a single image and return structured results."""
    print(f"\n🔍 Testing Image: {os.path.basename(image_path)}")
    if not os.path.exists(image_path):
        print(f"❌ Path does not exist: {image_path}")
        return {"error": "Invalid image path"}
        
    start_time = time.time()
    
    try:
        result = inference_engine.inference_pipeline(image_path)
        inference_time = (time.time() - start_time) * 1000

        if result is None:
            print("❌ Model inference failed.")
            return {"error": "Inference failed"}

        food_items = result.get("food_items", [])
        detections = result.get("detections", [])
        confidence = result.get("confidence", 0.0)

        # Output basic metrics
        print(f"⏱️  Inference Time: {inference_time:.2f} ms")
        print(f"🎯 Detections Count: {len(detections)}")
        print(f"🍽️  Detected Food: {', '.join(food_items)}")
        
        if len(detections) == 0:
            print("⚠️  No food objects were detected strongly.")
        
        # Analyze detection accuracy & debug info
        low_conf = []
        for det in detections:
            conf = det['confidence']
            print(f"   - Label: {det['name']} | Confidence: {conf:.2f}")
            if conf < 0.6:
                low_conf.append(det)
        
        if low_conf:
            print(f"⚠️  {len(low_conf)} items detected with low confidence (< 0.60)")
            
        # Optional: Visualization and Annotations
        if save_images:
            annotate_and_save(image_path, detections, outputs_dir)

        return {
            "image": os.path.basename(image_path),
            "food_items": food_items,
            "detections": detections,
            "overall_confidence": confidence,
            "inference_time_ms": round(inference_time, 2)
        }
        
    except Exception as e:
        print(f"❌ Unexpected Error during inference: {e}")
        traceback.print_exc()
        return {"error": str(e)}

def annotate_and_save(image_path, detections, outputs_dir):
    """Draw bounding boxes and labels onto the image and save to outputs/."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"⚠️ Cannot open image file for annotation: {image_path}")
            return
            
        # Draw each detection
        for det in detections:
            bbox = det.get('bbox', [])
            if len(bbox) == 4:
                x1, y1, x2, y2 = [int(v) for v in bbox]
                label = f"{det.get('name', 'Object')} {det.get('confidence', 0.0):.2f}"
                
                # Rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Text Background
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
                
                # Text
                cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

        filename, ext = os.path.splitext(os.path.basename(image_path))
        output_path = os.path.join(outputs_dir, f"{filename}_annotated{ext}")
        cv2.imwrite(output_path, img)
        print(f"🖼️  Saved annotated image to: {output_path}")
        
    except Exception as e:
        print(f"⚠️ Failed to save annotated image: {e}")


def batch_test_folder(inference_engine, test_folder, outputs_dir, save_images=False):
    """Loop through a folder of images and run the inference test on them."""
    print("\n" + "="*60)
    print(f"📂 BATCH TESTING: {test_folder}")
    print("="*60)
    
    valid_exts = {'.png', '.jpg', '.jpeg', '.bmp'}
    files_to_test = [os.path.join(test_folder, f) for f in os.listdir(test_folder) 
                     if os.path.splitext(f)[1].lower() in valid_exts]
    
    if not files_to_test:
        print(f"⚠️ No valid images found in {test_folder}")
        return []
        
    print(f"Found {len(files_to_test)} images for testing.")
    
    results = []
    total_time = 0.0
    failed_images = 0
    
    for img_path in files_to_test:
        res = process_single_image(inference_engine, img_path, outputs_dir, save_images)
        results.append(res)
        
        if 'error' in res:
            failed_images += 1
        else:
            total_time += res.get('inference_time_ms', 0)

    print("\n" + "-"*60)
    print("📊 BATCH TEST SUMMARY")
    print(f"Total Images: {len(files_to_test)}")
    print(f"Failed Detections/Errors: {failed_images}")
    if len(files_to_test) - failed_images > 0:
        avg_time = total_time / (len(files_to_test) - failed_images)
        print(f"Avg Inference Time per image: {avg_time:.2f} ms")
    print("-"*60 + "\n")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Deep Verification of Trained Model for NutriFy")
    parser.add_argument("--image", type=str, help="Path to a single image to test.")
    parser.add_argument("--dir", type=str, default="test_images", help="Path to a folder of images to test.")
    parser.add_argument("--save_json", action="store_true", help="Save test results to a JSON file.")
    parser.add_argument("--save_images", action="store_true", default=True, help="Annotate and save results as an image file.")
    
    args = parser.parse_args()
    
    # 1. Directory Structure Setup
    test_images_dir, outputs_dir = setup_directories()
    
    # Check overrides
    if args.dir != "test_images":
        test_images_dir = args.dir
        
    # 2. Loading Test
    engine = initialize_models()
    if not engine:
        print("❌ Testing aborted. Model failed to load.")
        sys.exit(1)
        
    all_results = []
    
    # 3. Execution
    if args.image:
        result = process_single_image(engine, args.image, outputs_dir, save_images=args.save_images)
        all_results.append(result)
    else:
        all_results = batch_test_folder(engine, test_images_dir, outputs_dir, save_images=args.save_images)
        
    # 4. Save JSON Report
    if args.save_json or True: # Keep True to always save by default based on spec requirement
        json_path = os.path.join(outputs_dir, "test_results.json")
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=4)
            print(f"💾 Saved comprehensive results to: {json_path}")
        except Exception as e:
            print(f"⚠️ Error saving JSON: {e}")

if __name__ == "__main__":
    main()
