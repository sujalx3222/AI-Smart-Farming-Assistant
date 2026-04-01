# ==============================================================================
# 🌾 CROP RECOMMENDATION MODEL — SINGLE-CELL GOOGLE COLAB TRAINING SCRIPT
# ==============================================================================
# Instructions:
# 1. Open Google Colab (https://colab.research.google.com/)
# 2. Click "New Notebook"
# 3. Paste ALL of this code into a single cell and RUN it.
# 4. Upload 'Crop_recommendation.csv' when prompted.
# 5. Download the files at the end and move them to your FYP\backend folder.
# ==============================================================================

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from google.colab import files
import os

print("--- 🌾 Step 1: Uploading Dataset ---")
print("Please select 'Crop_recommendation.csv' from your Downloads folder.")
uploaded = files.upload()

if not uploaded:
    print("❌ Error: No file uploaded. Please run the cell again.")
else:
    file_name = list(uploaded.keys())[0]
    print(f"✅ Successfully uploaded: {file_name}")

    # --- Step 2: Load and Prepare Data ---
    print("\n--- 📦 Step 2: Preparing Data ---")
    df = pd.read_csv(file_name)
    
    # Feature engineering
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[features].values
    y = df['label'].values
    
    # Label encoding
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    print(f"✅ Found {len(le.classes_)} unique crops.")
    print(f"✅ Data shape: {df.shape}")

    # Split data (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

    # --- Step 3: Train Model (High Accuracy) ---
    print("\n--- 🌲 Step 3: Training Random Forest (Strong Accuracy) ---")
    # Using we-ll tuned Random Forest for maximum robustness
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")
    
    # --- Step 4: Show Evaluation Visuals ---
    print("\n--- 📊 Step 4: Evaluation Results ---")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Plot Confusion Matrix
    fig, ax = plt.subplots(figsize=(15, 12))
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
    disp.plot(ax=ax, xticks_rotation=90, cmap="YlGnBu")
    plt.title(f"Confusion Matrix (Accuracy: {accuracy*100:.2f}%)")
    plt.savefig('confusion_matrix.png')
    plt.show()

    # --- Step 5: Save and Download ---
    print("\n--- 💾 Step 5: Saving and Downloading Files ---")
    joblib.dump(model, 'crop_model.pkl')
    joblib.dump(le, 'crop_encoder.pkl')
    
    print("✅ Files saved: crop_model.pkl, crop_encoder.pkl")
    print("⬇️ Initiating browser downloads...")
    
    files.download('crop_model.pkl')
    files.download('crop_encoder.pkl')
    files.download('confusion_matrix.png')
    
    print("\n==================================================")
    print("🎉 CONGRATULATIONS! Training Complete.")
    print("Move 'crop_model.pkl' and 'crop_encoder.pkl' to your:")
    print(r"C:\Users\User\Desktop\FYP\backend folder.")
    print("==================================================")
