"""
Diagnostic script to check the leaf disease model for issues.
"""
import os
import sys
import json
import numpy as np

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'leaf_disease_model.keras')
METADATA_PATH = os.path.join(BASE_DIR, 'leaf_disease_metadata.json')

print("=" * 60)
print("  LEAF DISEASE MODEL DIAGNOSTIC")
print("=" * 60)

# 1. Check metadata
print("\n[1] METADATA CHECK:")
with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)
classes = metadata.get('classes', [])
print(f"  Metadata classes ({len(classes)}):")
for i, c in enumerate(classes):
    print(f"    [{i:2d}] {c}")
print(f"  Metadata img_size: {metadata.get('img_size')}")

# 2. Load model and check architecture
print("\n[2] MODEL CHECK:")
model = tf.keras.models.load_model(MODEL_PATH)
output_shape = model.output_shape
input_shape = model.input_shape
print(f"  Model input shape:  {input_shape}")
print(f"  Model output shape: {output_shape}")
print(f"  Model output units: {output_shape[-1]}")

num_model_classes = output_shape[-1]
num_metadata_classes = len(classes)
if num_model_classes != num_metadata_classes:
    print(f"\n  *** CRITICAL MISMATCH! Model={num_model_classes}, Metadata={num_metadata_classes} ***")
else:
    print(f"\n  OK - Class count matches: {num_model_classes}")

# 3. Test with a dummy random image
print("\n[3] DUMMY PREDICTION TEST (random noise image):")
dummy = np.random.randint(0, 256, (1, 224, 224, 3), dtype=np.uint8).astype('float32')
preds = model.predict(dummy, verbose=0)[0]
print(f"  Prediction shape: {preds.shape}")
print(f"  Sum of probabilities: {preds.sum():.4f}")
print(f"  Max probability: {preds.max()*100:.2f}% at index {np.argmax(preds)}")
if len(classes) == num_model_classes:
    print(f"  Predicted class: {classes[np.argmax(preds)]}")

# 4. Check all probabilities
print("\n[4] ALL PROBABILITIES (random noise image):")
for i, prob in enumerate(preds):
    label = classes[i] if i < len(classes) else f"UNKNOWN_CLASS_{i}"
    bar = '#' * int(prob * 100 / 2)
    print(f"  [{i:2d}] {label:50s}: {prob*100:6.2f}% {bar}")

# 5. Test with different colored images to detect bias
print("\n[5] BIAS TEST (uniform color images):")
for color_name, color_val in [("Black", [0,0,0]), ("White", [255,255,255]), ("Green", [0,128,0]), ("Brown", [139,69,19])]:
    test_img = np.full((1, 224, 224, 3), color_val, dtype='float32')
    p = model.predict(test_img, verbose=0)[0]
    idx = np.argmax(p)
    label = classes[idx] if idx < len(classes) else f"UNKNOWN_{idx}"
    print(f"  {color_name:6s} image -> {label} ({p[idx]*100:.1f}%)")

# 6. Test with a real leaf-like image (try to find one)
print("\n[6] REAL IMAGE TEST:")
test_dirs = [
    os.path.join(BASE_DIR, 'leaf_disease_data', 'Datasets'),
    os.path.join(BASE_DIR, 'leaf_disease_data'),
]
found_images = []
for test_dir in test_dirs:
    if os.path.exists(test_dir):
        for root, dirs, files in os.walk(test_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    found_images.append(os.path.join(root, f))
                    if len(found_images) >= 10:
                        break
            if len(found_images) >= 10:
                break

if found_images:
    from PIL import Image
    for img_path in found_images[:5]:
        try:
            img = Image.open(img_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img, dtype='float32')
            img_array = np.expand_dims(img_array, axis=0)
            p = model.predict(img_array, verbose=0)[0]
            idx = np.argmax(p)
            label = classes[idx] if idx < len(classes) else f"UNKNOWN_{idx}"
            folder = os.path.basename(os.path.dirname(img_path))
            print(f"  {os.path.basename(img_path)[:30]:30s} (folder: {folder:30s}) -> {label} ({p[idx]*100:.1f}%)")
        except Exception as e:
            print(f"  Error with {img_path}: {e}")
else:
    print("  No test images found in leaf_disease_data directory")

# 7. Model layer info
print("\n[7] MODEL ARCHITECTURE (last 8 layers):")
for layer in model.layers[-8:]:
    config = layer.get_config()
    print(f"  {layer.name:30s}: {layer.__class__.__name__:25s} -> output: {layer.output_shape}")

# 8. Check if preprocessing is built into the model
print("\n[8] PREPROCESSING CHECK:")
has_preprocess = False
for layer in model.layers:
    name_lower = layer.name.lower()
    if 'preprocess' in name_lower or 'rescal' in name_lower or 'normalization' in name_lower:
        print(f"  Found preprocessing layer: {layer.name} ({layer.__class__.__name__})")
        has_preprocess = True
if not has_preprocess:
    print("  WARNING: No preprocessing layer found in model!")
    print("  The prediction script may need to add manual preprocessing.")

print("\n" + "=" * 60)
print("  DIAGNOSTIC COMPLETE")
print("=" * 60)
