import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def evaluate():
    try:
        print("Loading data...")
        df = pd.read_csv('c:/Users/User/Desktop/FYP/Crop_recommendation.csv')
        X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
        y = df['label']
        
        print("Loading model...")
        model = joblib.load('c:/Users/User/Desktop/FYP/crop_model.pkl')
        le = joblib.load('c:/Users/User/Desktop/FYP/crop_encoder.pkl')
        
        print("Encoding labels...")
        y_encoded = le.transform(y)
        
        print("Splitting data...")
        _, X_test, _, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        print("Predicting...")
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Final Accuracy: {accuracy * 100:.2f}%")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    evaluate()
