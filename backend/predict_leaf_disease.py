"""
Leaf Disease Prediction Script
Loads the trained MobileNetV2 model and predicts disease class for new leaf images.
Supports 15 classes: Tomato, Potato, and Pepper diseases.
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

try:
    import tensorflow as tf
except ImportError:
    tf = None


# ============================================================
# Configuration
# ============================================================
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

MODEL_PATH = os.path.join(BASE_DIR, 'leaf_disease_model.keras')
METADATA_PATH = os.path.join(BASE_DIR, 'leaf_disease_metadata.json')

IMG_SIZE = 224

# ============================================================
# Disease Information for all 15 classes
# ============================================================
DISEASE_MAPPING = {
    'Pepper__bell___Bacterial_spot': {
        'name': 'Pepper Bell - Bacterial Spot',
        'description': 'Bacterial infection caused by Xanthomonas that creates small, dark, water-soaked lesions on pepper leaves and fruit.',
        'treatment': 'Apply copper-based bactericides. Remove and destroy infected plants. Avoid overhead irrigation and rotate crops every 2-3 years.'
    },
    'Pepper__bell___healthy': {
        'name': 'Pepper Bell - Healthy',
        'description': 'The pepper leaf appears healthy with no visible signs of disease.',
        'treatment': 'No treatment needed. Continue regular watering, fertilization, and pest monitoring.'
    },
    'Potato___Early_blight': {
        'name': 'Potato - Early Blight',
        'description': 'Fungal disease caused by Alternaria solani. Creates dark, concentric "target-like" rings on older leaves first.',
        'treatment': 'Apply chlorothalonil or mancozeb fungicides. Remove infected leaves immediately. Ensure proper plant spacing for airflow.'
    },
    'Potato___Late_blight': {
        'name': 'Potato - Late Blight',
        'description': 'Highly destructive disease caused by Phytophthora infestans. Can destroy entire crops within days if untreated.',
        'treatment': 'Apply metalaxyl or copper fungicides IMMEDIATELY. Remove and burn all infected plants. Do NOT compost infected material.'
    },
    'Potato___healthy': {
        'name': 'Potato - Healthy',
        'description': 'The potato leaf shows no signs of disease and appears healthy.',
        'treatment': 'No treatment needed. Maintain proper irrigation schedules and monitor for early signs of blight.'
    },
    'Tomato_Bacterial_spot': {
        'name': 'Tomato - Bacterial Spot',
        'description': 'Caused by Xanthomonas bacteria. Creates small, dark, greasy-looking spots on leaves that may have yellow halos.',
        'treatment': 'Apply copper sprays early in the season. Remove infected leaves. Avoid working with wet plants to prevent spread.'
    },
    'Tomato_Early_blight': {
        'name': 'Tomato - Early Blight',
        'description': 'Fungal disease (Alternaria solani) causing dark concentric rings on lower leaves, spreading upward over time.',
        'treatment': 'Apply fungicides containing chlorothalonil. Mulch around plants to prevent soil splash. Remove lower infected leaves.'
    },
    'Tomato_Late_blight': {
        'name': 'Tomato - Late Blight',
        'description': 'Devastating disease caused by Phytophthora infestans. Large, irregular water-soaked patches appear rapidly.',
        'treatment': 'Apply copper-based fungicides immediately. Remove and destroy ALL infected plants. This disease spreads extremely fast.'
    },
    'Tomato_Leaf_Mold': {
        'name': 'Tomato - Leaf Mold',
        'description': 'Fungal disease (Passalora fulva) causing pale green to yellow spots on upper leaf surface with olive-green mold underneath.',
        'treatment': 'Improve ventilation and reduce humidity. Apply fungicides like mancozeb. Avoid wetting leaves during watering.'
    },
    'Tomato_Septoria_leaf_spot': {
        'name': 'Tomato - Septoria Leaf Spot',
        'description': 'Fungal disease causing small, circular spots with dark borders and gray centers on lower leaves.',
        'treatment': 'Remove infected lower leaves. Apply copper or chlorothalonil fungicides. Mulch to prevent rain splash from soil.'
    },
    'Tomato_Spider_mites_Two_spotted_spider_mite': {
        'name': 'Tomato - Spider Mites',
        'description': 'Tiny pests that suck sap from leaves causing yellow stippling, webbing, and eventual leaf death.',
        'treatment': 'Spray with neem oil or insecticidal soap. Increase humidity around plants. Introduce predatory mites as biological control.'
    },
    'Tomato__Target_Spot': {
        'name': 'Tomato - Target Spot',
        'description': 'Fungal disease (Corynespora cassiicola) causing brown lesions with concentric rings resembling a target.',
        'treatment': 'Apply fungicides containing azoxystrobin. Improve air circulation. Remove and destroy heavily infected leaves.'
    },
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {
        'name': 'Tomato - Yellow Leaf Curl Virus',
        'description': 'Viral disease transmitted by whiteflies causing upward leaf curling, yellowing, and stunted growth.',
        'treatment': 'No cure exists for infected plants. Control whiteflies with insecticides or yellow sticky traps. Remove infected plants immediately.'
    },
    'Tomato__Tomato_mosaic_virus': {
        'name': 'Tomato - Mosaic Virus',
        'description': 'Viral disease causing mottled light and dark green patterns on leaves with possible leaf curling and distortion.',
        'treatment': 'No cure exists. Remove and destroy infected plants. Disinfect tools with 10% bleach solution. Wash hands before handling plants.'
    },
    'Tomato_healthy': {
        'name': 'Tomato - Healthy',
        'description': 'The tomato leaf appears healthy with no visible signs of disease or pest damage.',
        'treatment': 'No treatment needed. Continue regular care with proper watering, fertilization, and crop rotation practices.'
    }
}


# ============================================================
# Core Functions
# ============================================================
def load_model_and_metadata():
    """Load the trained model and metadata."""
    if tf is None:
        raise ImportError("TensorFlow is not installed. Leaf disease detection is currently unavailable on this Python version.")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            f"Please run train_leaf_disease_model.py first."
        )

    print("Loading leaf disease model...")
    model = tf.keras.models.load_model(MODEL_PATH)

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {
            'classes': ['Unknown'],
            'img_size': IMG_SIZE
        }

    print(f"Model loaded with {len(metadata.get('classes', []))} classes.")
    return model, metadata


def preprocess_image(image_path, img_size=IMG_SIZE):
    """Load and preprocess a single image for prediction.
    NOTE: The model already has preprocess_input built into its layers,
    so we only need to resize and pass raw [0, 255] pixel values."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((img_size, img_size))
    img_array = np.array(img, dtype='float32')
    # DO NOT apply preprocess_input here - the model does it internally
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array, img


def predict_single_image(model, metadata, image_path):
    """Predict disease class for a single image."""
    img_size = metadata.get('img_size', 224)
    classes = metadata.get('classes', ['Unknown'])

    img_array, original_img = preprocess_image(image_path, img_size)
    predictions = model.predict(img_array, verbose=0)[0]

    predicted_class_idx = np.argmax(predictions)
    raw_class = classes[predicted_class_idx]
    confidence = predictions[predicted_class_idx] * 100

    # Get readable disease info
    info = DISEASE_MAPPING.get(raw_class, {
        'name': raw_class.replace('_', ' ').replace('  ', ' ').strip(),
        'description': f'Detected condition: {raw_class}.',
        'treatment': 'Consult a local agricultural expert for specific treatment recommendations.'
    })

    result = {
        'image_path': image_path,
        'predicted_class': info['name'],
        'raw_label': raw_class,
        'confidence': float(confidence),
        'all_probabilities': {classes[i]: float(predictions[i] * 100) for i in range(len(classes))},
        'disease_info': info
    }

    return result, original_img


def predict_directory(model, metadata, directory_path):
    """Predict disease class for all images in a directory."""
    results = []
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

    for filename in sorted(os.listdir(directory_path)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_extensions:
            filepath = os.path.join(directory_path, filename)
            try:
                result, _ = predict_single_image(model, metadata, filepath)
                results.append(result)
            except Exception as e:
                print(f"  Error processing {filename}: {e}")

    return results


def print_prediction(result):
    """Pretty print a single prediction result."""
    print(f"\n  Image: {os.path.basename(result['image_path'])}")
    print(f"  Predicted: {result['predicted_class']} ({result['confidence']:.1f}% confidence)")
    print(f"  Description: {result['disease_info'].get('description', 'N/A')}")
    print(f"  Treatment: {result['disease_info'].get('treatment', 'N/A')}")
    print(f"  All probabilities:")
    for cls, prob in sorted(result['all_probabilities'].items(), key=lambda x: -x[1]):
        bar = '█' * int(prob / 2)
        print(f"    {cls:50s}: {prob:5.1f}% {bar}")


def save_prediction_visualization(results, save_path):
    """Save a visualization of predictions."""
    n = min(len(results), 10)
    if n == 0:
        return

    cols = min(5, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    for i in range(n):
        result = results[i]
        img = Image.open(result['image_path']).convert('RGB')
        axes[i].imshow(img)
        is_healthy = 'healthy' in result['raw_label'].lower()
        color = 'green' if is_healthy else 'red'
        axes[i].set_title(
            f"{result['predicted_class']}\n{result['confidence']:.1f}%",
            fontsize=10, color=color, fontweight='bold'
        )
        axes[i].axis('off')

    for i in range(n, len(axes)):
        axes[i].axis('off')

    plt.suptitle('Leaf Disease Predictions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Saved prediction visualization to {save_path}")


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("  LEAF DISEASE PREDICTION (15-Class Model)")
    print("=" * 60)

    model, metadata = load_model_and_metadata()
    print(f"  Classes: {metadata.get('classes')}")

    if len(sys.argv) >= 2:
        target = sys.argv[1]
        if os.path.isdir(target):
            print(f"\n  Predicting all images in: {target}")
            results = predict_directory(model, metadata, target)
            for result in results:
                print_prediction(result)
        elif os.path.isfile(target):
            result, _ = predict_single_image(model, metadata, target)
            print_prediction(result)
        else:
            print(f"  ERROR: Path not found: {target}")
    else:
        print("\n  Usage: python predict_leaf_disease.py <image_or_folder_path>")


if __name__ == '__main__':
    main()
