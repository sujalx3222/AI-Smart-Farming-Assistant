import pandas as pd
import numpy as np
import joblib
import os
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

def train_highly_accurate_crop_model():
    print("==================================================")
    print("🌾 ADVANCED CROP RECOMMENDATION MODEL TRAINING 🌾")
    print("==================================================")
    
    # 1. Dataset Loading
    # Using the exact dataset path you provided
    dataset_path = r"C:\Users\User\Downloads\Dataset\Crop_recommendation.csv"
    
    print(f"\n📂 Step 1: Loading dataset from: \n   {dataset_path}")
    
    if not os.path.exists(dataset_path):
        print(f"\n❌ ERROR: File not found at {dataset_path}")
        print("Please make sure 'Crop_recommendation.csv' is inside 'C:\\Users\\User\\Downloads\\Dataset\\'")
        return

    df = pd.read_csv(dataset_path)
    
    # Define features and target label
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[features].values
    y = df['label'].values
    
    # 2. Encode Labels
    print("\n🏷️ Step 2: Processing labels...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    num_classes = len(le.classes_)
    print(f"   Found {num_classes} unique crops in the dataset.")
    
    # 3. Train/Test Split
    print("\n✂️ Step 3: Splitting data (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # 4. Model Training (Optimized Random Forest for high accuracy)
    print("\n🚀 Step 4: Training Advanced Random Forest Classifier...")
    print("   (This might take a few seconds...)")
    start_time = time.time()
    
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
    training_time = time.time() - start_time
    print(f"   ✅ Training complete in {training_time:.2f} seconds!")
    
    # 5. Evaluate Accuracy
    print("\n📈 Step 5: Evaluating Model Accuracy...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("==================================================")
    print(f"🏆 FINAL TEST ACCURACY: {accuracy * 100:.2f}%")
    print("==================================================")
    
    if accuracy < 0.95:
        print("⚠️ Warning: Accuracy is lower than expected. Check the dataset quality.")
    else:
        print("✅ Excellent accuracy achieved!")

    # 6. Save the models correctly in the backend directory
    print("\n💾 Step 6: Saving Model Files...")
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(backend_dir, 'crop_model.pkl')
    encoder_path = os.path.join(backend_dir, 'crop_encoder.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(le, encoder_path)
    
    print(f"   ✅ Model saved to: {model_path}")
    print(f"   ✅ Encoder saved to: {encoder_path}")
    
    print("\n🎉 ALL DONE! The API is now ready to use the new accurate model.")

if __name__ == "__main__":
    train_highly_accurate_crop_model()
