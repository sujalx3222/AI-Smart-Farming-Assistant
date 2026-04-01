import os
import numpy as np
import json
import argparse
import sys
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ============================================================
# Smart Path Detection
# ============================================================
# Automatically finds the dataset whether you're on Kaggle, Colab, or Local
def get_best_dataset_path():
    possible_paths = [
        # Kaggle Path
        "/kaggle/input/new-plant-diseases-dataset/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)",
        # Colab/Local fallback paths
        "/content/leaf_disease_data/Datasets",
        "./leaf_disease_data/Datasets",
        "../leaf_disease_data/Datasets"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# ============================================================
# Configuration
# ============================================================
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# Outputs will always save to the current working directory (Kaggle/Colab friendly)
MODEL_SAVE_PATH = 'leaf_disease_model.keras'
METADATA_SAVE_PATH = 'leaf_disease_metadata.json'

IMG_SIZE = 224  # High detail for best accuracy
BATCH_SIZE = 32
EPOCHS = 50

# ============================================================
# Model Architecture (Strong Model)
# ============================================================
def build_strong_model(num_classes):
    """Builds a high-accuracy EfficientNetB0 Transfer Learning model."""
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base_model.trainable = False 

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model, base_model

# ============================================================
# Training Pipeline
# ============================================================
def run_training(dataset_path=None):
    if not dataset_path:
        dataset_path = get_best_dataset_path()
    
    print("=" * 60)
    print("  AGRISMART AI - STRONG MODEL TRAINING")
    print(f"  Dataset: {dataset_path}")
    print(f"  Architecture: EfficientNetB0")
    print("=" * 60)

    if not dataset_path or not os.path.exists(dataset_path):
        print(f"ERROR: Dataset not found. Please provide path via --dataset")
        return

    # 1. Image Generators (Memory Efficient)
    datagen = ImageDataGenerator(
        rotation_range=40, width_shift_range=0.3, height_shift_range=0.3,
        shear_range=0.2, zoom_range=0.3, horizontal_flip=True, 
        vertical_flip=True, fill_mode='nearest', brightness_range=[0.7, 1.3],
        validation_split=0.2
    )

    train_gen = datagen.flow_from_directory(
        dataset_path, target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE, class_mode='categorical', subset='training'
    )

    val_gen = datagen.flow_from_directory(
        dataset_path, target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE, class_mode='categorical', subset='validation'
    )

    num_classes = len(train_gen.class_indices)
    classes = list(train_gen.class_indices.keys())
    print(f"\nSuccessfully discovered {num_classes} classes!")

    # 2. Training
    model, base_model = build_strong_model(num_classes)
    
    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=8, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1),
        ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_accuracy', save_best_only=True, verbose=1)
    ]

    print("\n[Phase 1] Training classification head...")
    model.fit(train_gen, validation_data=val_gen, epochs=5, callbacks=callbacks)

    print("\n[Phase 2] Fine-tuning EfficientNet base model...")
    base_model.trainable = True
    for layer in base_model.layers[:100]: layer.trainable = False

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
                  loss='categorical_crossentropy', metrics=['accuracy'])

    model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS, callbacks=callbacks)

    # 3. Save Final Metadata
    with open(METADATA_SAVE_PATH, 'w') as f:
        json.dump({'classes': classes, 'img_size': IMG_SIZE, 'architecture': 'EfficientNetB0'}, f, indent=2)
    
    print(f"\nSUCCESS! Model saved to: {os.path.abspath(MODEL_SAVE_PATH)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default=None)
    # Ignore Jupyter flags
    args, _ = parser.parse_known_args()
    run_training(args.dataset)

