"""
Retrain Leaf Disease Model with the CORRECT dataset path.
The dataset at PlantVillage\PlantVillage has the proper 15 classes including Tomato_healthy.
Optimized for CPU training with MobileNetV2 (lightweight).
"""
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks

# ============================================================
# CONFIGURATION
# ============================================================
# CORRECT path - the nested PlantVillage folder with all 15 proper classes
DATASET_PATH = r"C:\Users\User\Downloads\archive (3)\PlantVillage\PlantVillage"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'leaf_disease_model.keras')
METADATA_SAVE_PATH = os.path.join(BASE_DIR, 'leaf_disease_metadata.json')

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_PHASE1 = 8   # Train classification head (frozen base)
EPOCHS_PHASE2 = 5   # Fine-tune top layers of base model
VAL_SPLIT = 0.2

def retrain():
    print("=" * 60)
    print("  LEAF DISEASE MODEL - RETRAINING (FIXED DATASET)")
    print("=" * 60)

    # 1. Verify dataset
    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        return

    class_folders = [d for d in sorted(os.listdir(DATASET_PATH)) 
                     if os.path.isdir(os.path.join(DATASET_PATH, d))]
    print(f"\nDataset path: {DATASET_PATH}")
    print(f"Found {len(class_folders)} class folders:")
    for i, folder in enumerate(class_folders):
        count = len(os.listdir(os.path.join(DATASET_PATH, folder)))
        print(f"  [{i:2d}] {folder}: {count} images")

    # Verify Tomato_healthy exists
    if 'Tomato_healthy' not in class_folders:
        print("\nERROR: 'Tomato_healthy' folder not found! Wrong dataset path.")
        return
    if 'PlantVillage' in class_folders:
        print("\nERROR: Nested 'PlantVillage' folder detected! Wrong dataset path.")
        return
    print("\n[OK] Dataset structure verified - all 15 classes present")

    # 2. Load dataset
    print("\n[Step 1] Loading dataset...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_PATH,
        validation_split=VAL_SPLIT,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='categorical'
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_PATH,
        validation_split=VAL_SPLIT,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='categorical'
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"\nClasses ({num_classes}): {class_names}")

    # Performance optimization
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # 3. Build Model (MobileNetV2 with built-in preprocessing)
    print("\n[Step 2] Building MobileNetV2 model...")

    data_augmentation = models.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.1),
    ])

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze for Phase 1

    # Model with preprocessing BUILT IN
    inputs = layers.Input(shape=(224, 224, 3))
    x = data_augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)  # [0,255] -> [-1,1]
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs, outputs)
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    print(f"  Total parameters: {model.count_params():,}")
    print(f"  Trainable parameters: {sum(tf.keras.backend.count_params(w) for w in model.trainable_weights):,}")

    # 4. Phase 1: Train classification head
    print(f"\n[Step 3] Phase 1 - Training head ({EPOCHS_PHASE1} epochs)...")
    start = time.time()

    early_stop = callbacks.EarlyStopping(
        monitor='val_accuracy', patience=5, restore_best_weights=True, verbose=1
    )
    reduce_lr = callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.2, patience=2, verbose=1
    )

    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_PHASE1,
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )

    phase1_time = time.time() - start
    phase1_acc = max(history1.history.get('val_accuracy', [0]))
    print(f"\n  Phase 1 complete in {phase1_time/60:.1f} minutes")
    print(f"  Best validation accuracy: {phase1_acc*100:.1f}%")

    # 5. Phase 2: Fine-tune top layers of base model
    print(f"\n[Step 4] Phase 2 - Fine-tuning ({EPOCHS_PHASE2} epochs)...")
    base_model.trainable = True
    # Only fine-tune the top 30 layers
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    start2 = time.time()
    history2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_PHASE2,
        callbacks=[early_stop],
        verbose=1
    )

    phase2_time = time.time() - start2
    phase2_acc = max(history2.history.get('val_accuracy', [0]))
    print(f"\n  Phase 2 complete in {phase2_time/60:.1f} minutes")
    print(f"  Best validation accuracy: {phase2_acc*100:.1f}%")

    # 6. Save model and metadata
    print("\n[Step 5] Saving model and metadata...")
    model.save(MODEL_SAVE_PATH)

    metadata = {
        'classes': class_names,
        'img_size': 224,
        'num_classes': num_classes,
        'architecture': 'MobileNetV2'
    }
    with open(METADATA_SAVE_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"  Model saved: {MODEL_SAVE_PATH}")
    print(f"  Metadata saved: {METADATA_SAVE_PATH}")

    total_time = time.time() - start
    print("\n" + "=" * 60)
    print(f"  TRAINING COMPLETE!")
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"  Final accuracy: {phase2_acc*100:.1f}%")
    print(f"  Classes: {class_names}")
    print("=" * 60)
    print("\nRESTART your Django backend to load the new model!")

if __name__ == "__main__":
    retrain()
