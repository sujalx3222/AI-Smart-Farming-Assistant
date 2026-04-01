import os
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
import json
import matplotlib.pyplot as plt

# ==========================================
# 🚀 ADVANCED LEAF DISEASE TRAINING SCRIPT
# ==========================================
# Optimized for: C:\Users\User\Downloads\archive (3)\PlantVillage
# Using: MobileNetV2 (High Accuracy, Low Training Time)
# ==========================================

# ==========================================
# 🔍 SMART PATH DETECTION (ULTRA SEARCH)
# ==========================================
def find_dataset_path():
    print("🔎 Searching for dataset...")
    
    # 1. Potential Local Paths
    local_paths = [
        r"C:\Users\User\Downloads\archive (3)\PlantVillage",
        r"C:\Users\User\Downloads\archive (3)",
        "./PlantVillage"
    ]
    
    # 2. Check Kaggle Environments (Aggressive Tree Search)
    if os.path.exists("/kaggle/input"):
        print("📦 Detected Kaggle. Full Scan of /kaggle/input...")
        try:
            for root, dirs, files in os.walk("/kaggle/input"):
                # If a folder has > 5 subdirectories, it's very likely the class list
                if len(dirs) > 5:
                    # Double check if any of these dirs look like plant classes
                    if any("late_blight" in d.lower() or "healthy" in d.lower() or "spot" in d.lower() for d in dirs):
                        print(f"   ✅ FOUND dataset classes at: {root}")
                        return root
            
            # If we didn't find it by subdirs, check for the highest-level directory that isn't /kaggle/input
            for root, dirs, files in os.walk("/kaggle/input"):
                if "PlantVillage" in root:
                    print(f"   ✅ FOUND 'PlantVillage' folder at: {root}")
                    return root
        except Exception as e:
            print(f"   ⚠️ Error scanning Kaggle: {e}")

    # 3. Check Local Paths
    for p in local_paths:
        if os.path.exists(p):
            for root, dirs, files in os.walk(p):
                if len(dirs) > 5:
                    print(f"   ✅ FOUND local dataset at: {root}")
                    return root

    print("   ❌ Could not find a folder with the dataset classes.")
    print("   💡 TIP: Try printing os.listdir('/kaggle/input/datasets') in a separate cell to see what is inside.")
    return None

DATASET_PATH = find_dataset_path()
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_PHASE1 = 10 # Training the head
EPOCHS_PHASE2 = 10 # Fine-tuning (Optional, for higher accuracy)
VAL_SPLIT = 0.2

MODEL_SAVE_PATH = 'leaf_disease_model.keras'
METADATA_SAVE_PATH = 'leaf_disease_metadata.json'

def train_perfect_leaf_model():
    print("-" * 60)
    print("🌿 STARTING PERFECT LEAF DETECTION TRAINING 🌿")
    print("-" * 60)
    
    if not DATASET_PATH or not os.path.exists(DATASET_PATH):
        print(f"❌ ERROR: Dataset not found!")
        print("I searched in Kaggle Inputs, Colab, and your Local Downloads folder.")
        print("If you are on Kaggle, make sure you have ADDED the dataset to the session.")
        return

    print(f"📍 Using Dataset at: {DATASET_PATH}")

    # 2. Loading Dataset (Optimized with tf.data)
    print("\n📂 Step 1: Loading and Preprocessing Dataset...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_PATH,
        validation_split=VAL_SPLIT,
        subset="training",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='categorical'
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_PATH,
        validation_split=VAL_SPLIT,
        subset="validation",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='categorical'
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"\n✅ Found {num_classes} classes: {class_names}")

    # Autotuning for Performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # 3. Model Architecture (Transfer Learning)
    print("\n🚀 Step 2: Building Model Architecture (MobileNetV2)...")
    
    # Data Augmentation Layer (Helps prevent overfitting)
    data_augmentation = models.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.1),
    ])

    # Base Model (Pre-trained on ImageNet)
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base layers for initial training

    # Top Layers (Custom classification head)
    inputs = layers.Input(shape=(224, 224, 3))
    x = data_augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x) # Scale pixels to [-1, 1]
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # 4. Training Phase 1: Warming Up
    print("\n📈 Step 3: Phase 1 - Training classification Head (Warming Up)...")
    early_stop = callbacks.EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)
    reduce_lr = callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, verbose=1)

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_PHASE1,
        callbacks=[early_stop, reduce_lr]
    )

    # 5. Training Phase 2: Fine-tuning (Optional but recommended for perfection)
    print("\n🔥 Step 4: Phase 2 - Fine-tuning (Gaining Peak Accuracy)...")
    base_model.trainable = True
    
    # We use a very low learning rate for fine-tuning
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5), 
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    history_fine = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_PHASE2,
        callbacks=[early_stop]
    )

    # 6. Save Model and Metadata
    print("\n💾 Step 5: Saving Model and Metadata...")
    model.save(MODEL_SAVE_PATH)
    
    metadata = {
        'classes': class_names,
        'img_size': IMG_SIZE,
        'num_classes': num_classes,
        'architecture': 'MobileNetV2'
    }
    with open(METADATA_SAVE_PATH, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print("-" * 60)
    print(f"🎉 TRAINING COMPLETE!")
    print(f"👉 Model saved: {os.path.abspath(MODEL_SAVE_PATH)}")
    print(f"👉 Metadata saved: {os.path.abspath(METADATA_SAVE_PATH)}")
    print("-" * 60)

if __name__ == "__main__":
    train_perfect_leaf_model()
