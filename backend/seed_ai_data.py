import os
import django
import joblib
import numpy as np

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriculture_system.settings')
django.setup()

from api.models import CropRecommendation
from django.contrib.auth.models import User

# Load ML Models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'crop_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'crop_encoder.pkl')

def seed_data():
    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        admin_email = 'sujalmandal077@gmail.com'
        admin_password = 'Sujal@123'
        
        user = User.objects.filter(email=admin_email).first()
        if not user:
            from api.models import AdminProfile
            user = User.objects.create_superuser(username=admin_email, email=admin_email, password=admin_password)
            AdminProfile.objects.get_or_create(user=user)
            print(f"Admin user created: {admin_email} / {admin_password}")
        else:
            from api.models import AdminProfile
            AdminProfile.objects.get_or_create(user=user)
            # Update password just in case it was changed
            user.set_password(admin_password)
            user.save()
            print(f"Admin user updated: {admin_email}")
        
        # Some sample data points to predict
        samples = [
            [90, 42, 43, 20.8, 82, 6.5, 202], # Rice
            [80, 40, 40, 25.0, 70, 6.0, 150], # Maize
            [60, 50, 50, 22.0, 60, 7.0, 100], # Wheat
            [40, 30, 30, 30.0, 50, 5.5, 50],  # Grapes
        ]
        
        for s in samples:
            features = np.array([s])
            prediction = model.predict(features)
            crop = encoder.inverse_transform(prediction)[0]
            
            CropRecommendation.objects.create(
                user=user, nitrogen=s[0], phosphorus=s[1], potassium=s[2],
                temperature=s[3], humidity=s[4], soil_ph=s[5], rainfall=s[6],
                recommended_crop=crop
            )
            print(f"Created prediction: {crop}")
            
    except Exception as e:
        print(f"Error seeding data: {e}")

if __name__ == "__main__":
    seed_data()
