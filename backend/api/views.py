from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import *
from .serializers import *
import joblib
import numpy as np
import os
import time

# Load ML Models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'crop_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'crop_encoder.pkl')

try:
    crop_model = joblib.load(MODEL_PATH)
    crop_encoder = joblib.load(ENCODER_PATH)
except Exception as e:
    print(f"Error loading AI models: {e}")
    crop_model = None
    crop_encoder = None

# Lazy loading for leaf disease model (TF models are slow to load on CPU)
leaf_model = None
leaf_metadata = None
_leaf_model_loaded = False

def get_leaf_model():
    global leaf_model, leaf_metadata, _leaf_model_loaded
    if not _leaf_model_loaded:
        try:
            import predict_leaf_disease
            print("Loading leaf disease model (first request)...")
            leaf_model, leaf_metadata = predict_leaf_disease.load_model_and_metadata()
            print("Leaf disease model loaded successfully!")
        except Exception as e:
            print(f"Error loading leaf disease model: {e}")
            leaf_model = None
            leaf_metadata = None
        _leaf_model_loaded = True
    return leaf_model, leaf_metadata

class RegisterView(views.APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        phone = request.data.get('phone')
        location = request.data.get('location')

        if not all([name, email, password]):
            return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({'detail': 'Password must be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=email).exists():
            return Response({'detail': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        FarmerProfile.objects.create(user=user, phone=phone, location=location)

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(views.APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)
        if user:
            # Generate JWT Token
            refresh = RefreshToken.for_user(user)
            
            # Determine role
            role = 'farmer'
            if hasattr(user, 'admin_profile'):
                role = 'admin'
            
            return Response({
                'refresh': str(refresh),
                'token': str(refresh.access_token), 
                'user': user.first_name or user.username,
                'user_id': user.id,
                'role': role,
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

CROP_INFO = {
    'rice': {'description': 'A staple cereal grain, primarily grown in submerged fields. High water requirement.', 'season': 'Kharif (Monsoon)', 'duration': '120 days', 'yield': '3.5 - 5.0 tons/ha'},
    'maize': {'description': 'A versatile cereal grain used for food, fodder, and industrial products.', 'season': 'Kharif/Rabi', 'duration': '100 days', 'yield': '4.0 - 6.0 tons/ha'},
    'chickpea': {'description': 'A high-protein pulse crop that thrives in cool, dry climates.', 'season': 'Rabi (Winter)', 'duration': '110 days', 'yield': '1.5 - 2.5 tons/ha'},
    'kidneybeans': {'description': 'Commonly known as Rajma, it is a rich source of protein and fiber.', 'season': 'Rabi (Winter)', 'duration': '90 days', 'yield': '1.2 - 2.0 tons/ha'},
    'pigeonpeas': {'description': 'A perennial legume commonly used in dals across South Asia.', 'season': 'Kharif', 'duration': '180 days', 'yield': '1.0 - 1.8 tons/ha'},
    'mothbeans': {'description': 'Extremely drought-resistant legume, useful for arid regions.', 'season': 'Kharif', 'duration': '80 days', 'yield': '0.5 - 0.8 tons/ha'},
    'mungbean': {'description': 'A short-duration crop that can be grown between major seasons.', 'season': 'Summer/Kharif', 'duration': '70 days', 'yield': '0.8 - 1.2 tons/ha'},
    'blackgram': {'description': 'Highly nutritious pulse, often used for making fermented foods.', 'season': 'Kharif', 'duration': '85 days', 'yield': '1.0 - 1.5 tons/ha'},
    'lentil': {'description': 'A lens-shaped pulse known for its quick cooking time and nutritional value.', 'season': 'Rabi (Winter)', 'duration': '110 days', 'yield': '1.2 - 1.8 tons/ha'},
    'pomegranate': {'description': 'A fruit-bearing shrub valued for its nutrient-rich red seeds.', 'season': 'Year-round', 'duration': '3 years to maturity', 'yield': '15 - 20 tons/ha'},
    'banana': {'description': 'A tropical fruit crop that requires high humidity and steady rainfall.', 'season': 'Year-round', 'duration': '12 months', 'yield': '30 - 50 tons/ha'},
    'mango': {'description': 'The king of fruits, thrives in tropical and subtropical climates.', 'season': 'Summer', 'duration': '5 years to maturity', 'yield': '10 - 15 tons/ha'},
    'grapes': {'description': 'Grown in temperate or subtropical regions, primarily for fruit or wine.', 'season': 'Winter/Spring', 'duration': '3 years to maturity', 'yield': '20 - 25 tons/ha'},
    'watermelon': {'description': 'A popular summer fruit with high water content and sweetness.', 'season': 'Summer', 'duration': '90 days', 'yield': '25 - 40 tons/ha'},
    'muskmelon': {'description': 'A sweet, fragrant melon that grows well in warm, sandy soils.', 'season': 'Summer', 'duration': '80 days', 'yield': '15 - 25 tons/ha'},
    'apple': {'description': 'Temperatures and altitudes are critical for these crisp, sweet fruits.', 'season': 'Winter/Spring', 'duration': '5 years to maturity', 'yield': '20 - 30 tons/ha'},
    'orange': {'description': 'Citrus fruit known for high Vitamin C, grows best in subtropical areas.', 'season': 'Winter', 'duration': '4 years to maturity', 'yield': '20 - 30 tons/ha'},
    'papaya': {'description': 'Fast-growing fruit tree that produces year-round in tropical climates.', 'season': 'Year-round', 'duration': '9 months', 'yield': '40 - 60 tons/ha'},
    'coconut': {'description': 'Lush coastal palm providing water, milk, and oil.', 'season': 'Year-round', 'duration': '6 years to maturity', 'yield': '80-100 nuts/tree/year'},
    'cotton': {'description': 'Natural fiber crop that is a major cash crop for many farmers.', 'season': 'Kharif', 'duration': '160 days', 'yield': '2.0 - 3.5 tons/ha'},
    'jute': {'description': 'Long, soft, shiny plant fiber used for making strong threads.', 'season': 'Kharif', 'duration': '120 days', 'yield': '2.5 - 3.0 tons/ha'},
    'coffee': {'description': 'A major plantation crop that grows best in shade at high altitudes.', 'season': 'Year-round', 'duration': '3 years to maturity', 'yield': '0.8 - 1.2 tons/ha'}
}

class CropRecommendationView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        n = float(request.data.get('n'))
        p = float(request.data.get('p'))
        k = float(request.data.get('k'))
        temp = float(request.data.get('temperature'))
        hum = float(request.data.get('humidity'))
        ph = float(request.data.get('ph'))
        rain = float(request.data.get('rainfall'))

        # Input Validation for Realistic Ranges
        validation_errors = []
        if not (0 <= n <= 200): validation_errors.append("Nitrogen (0-200)")
        if not (0 <= p <= 200): validation_errors.append("Phosphorus (0-200)")
        if not (0 <= k <= 300): validation_errors.append("Potassium (0-300)")
        if not (-10 <= temp <= 60): validation_errors.append("Temperature (-10 to 60°C)")
        if not (0 <= hum <= 100): validation_errors.append("Humidity (0-100%)")
        if not (0 <= ph <= 14): validation_errors.append("Soil pH (0-14)")
        if not (0 <= rain <= 1000): validation_errors.append("Rainfall (0-1000mm)")

        if validation_errors:
            return Response({
                'detail': 'Unrealistic environmental values detected.',
                'invalid_fields': validation_errors,
                'recommended_crop': 'Invalid Input (Out of Range)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # ML-based crop recommendation
        if crop_model and crop_encoder:
            try:
                features = np.array([[n, p, k, temp, hum, ph, rain]])
                prediction = crop_model.predict(features)
                crop = crop_encoder.inverse_transform(prediction)[0]
            except Exception as e:
                print(f"Prediction error: {e}")
                crop = "rice" # Fallback
        else:
            crop = "rice" # Fallback logic
            if n > 50 and p > 50: crop = "maize"
            if temp > 30: crop = "mango"

        # Crop Information Mapping
        crop_data = {
            "Rice": {
                "desc": "Rice is a staple crop that grows best in standing water and high clay-content soil.",
                "market": "High - Globally in demand, especially in local markets.",
                "time": "4 - 6 Months",
                "care": "Maintain consistent water levels and apply urea in three splits."
            },
            "Maize": {
                "desc": "Maize (Corn) is a versatile cereal that requires plenty of sun and moderate water.",
                "market": "Steady - Used both for food and livestock feed.",
                "time": "3 - 4 Months",
                "care": "Ensure the soil is rich in nitrogen and maintain spacing for pollination."
            },
            "Wheat": {
                "desc": "Wheat is a cool-weather grass that produces high-value grains.",
                "market": "Constant - High demand in the flour and bakery industry.",
                "time": "5 - 7 Months",
                "care": "Require 4-6 irrigations during the growing cycle, especially at the jointing stage."
            },
            "Jute": {
                "desc": "Jute is a natural fiber crop that thrives in alluvium soil and hot, humid climates.",
                "market": "Specialized - Used for high-quality eco-friendly packaging.",
                "time": "4 Months",
                "care": "Requires heavy monsoon rains and standing water for the retting process."
            }
        }

        # Handle unknown crops
        details = crop_data.get(crop.capitalize(), {
            "desc": f"{crop.capitalize()} is a suitable crop for your soil and climate.",
            "market": "Growth potential available.",
            "time": "Dependent on variety",
            "care": "Follow standard agricultural practices for your region."
        })

        CropRecommendation.objects.create(
            user=user, nitrogen=n, phosphorus=p, potassium=k,
            temperature=temp, humidity=hum, soil_ph=ph, rainfall=rain,
            recommended_crop=crop
        )
        return Response({
            'recommended_crop': crop,
            'details': details
        }, status=status.HTTP_201_CREATED)

class SoilIdentificationView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        ph = float(request.data.get('ph'))
        moi = float(request.data.get('moisture'))
        n = float(request.data.get('nitrogen'))
        p = float(request.data.get('phosphorus'))
        k = float(request.data.get('potassium'))

        # Backend Validation for Realistic Ranges
        if not (0 <= ph <= 14) or not (0 <= moi <= 100):
            return Response({
                'detail': 'Unrealistic soil values detected (pH: 0-14, Moisture: 0-100%)',
                'soil_type': 'Invalid Input'
            }, status=status.HTTP_400_BAD_REQUEST)

        if ph < 6:
            soil_type = "Acidic Soil"
            crops = ["Potatoes", "Blueberries", "Sweet Potatoes", "Cranberries"]
            tips = "The soil is too acidic. Add **agricultural lime** or **wood ash** to raise the pH level. Avoid using ammonium-based fertilizers."
        elif ph > 7.5:
            soil_type = "Alkaline Soil"
            crops = ["Broccoli", "Cabbage", "Cauliflower", "Asparagus"]
            tips = "The soil is too alkaline. Add **elemental sulfur**, **peat moss**, or **composted manure** to lower the pH level."
        else:
            soil_type = "Loamy / Neutral Soil"
            crops = ["Tomatoes", "Lettuce", "Beans", "Peas", "Carrots"]
            tips = "This is the ideal soil range for most crops. Maintain quality with periodic **organic compost** additions."

        SoilTypeIdentification.objects.create(
            user=user, soil_ph=ph, soil_moisture=moi,
            nitrogen=n, phosphorus=p, potassium=k,
            soil_type_result=soil_type
        )
        return Response({
            'soil_type': soil_type,
            'recommended_crops': crops,
            'management_tips': tips
        }, status=status.HTTP_201_CREATED)

class VegetableRecommendationView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        temp = float(request.data.get('temperature'))
        season = request.data.get('season')
        soil = request.data.get('soil_type')
        # Backend Validation
        if not (-10 <= temp <= 60):
            return Response({'detail': 'Unrealistic temperature detected.'}, status=status.HTTP_400_BAD_REQUEST)

        # Intelligent Temperature-First Selection Logic
        if temp < 18:
            # Cool weather crops
            veg = "Cabbage"
            details = {
                "description": "Cabbage thrives in cool environments and rich, moist soil.",
                "suitability": f"Although you selected {season}, your current temperature of {temp}°C is actually suited for cool-climate vegetables like Cabbage.",
                "tips": "Harvest when heads are firm. Use organic compost to maintain steady nutrient levels.",
                "benefit": "Powerful antioxidant properties that support immune health."
            }
        elif 18 <= temp <= 30:
            # Warm weather crops
            if season == "Summer" or season == "Spring":
                veg = "Tomato"
                details = {
                    "description": "Tomatoes love the sun and balanced warmth (18-30°C).",
                    "suitability": f"The mild {temp}°C temperature and {season} light levels are ideal for fruit maturity.",
                    "tips": "Remove suckers (side shoots) to focus the plant's energy on fruit production.",
                    "benefit": "High in Lycopene and potassium, essential for skin and heart health."
                }
            elif season == "Rainy" or season == "Monsoon":
                veg = "Cucumber"
                details = {
                    "description": "Cucumbers are high-water content vegetables that thrive in humid, rainy conditions.",
                    "suitability": f"The abundance of water during the {season} season and steady {temp}°C temperature perfect for succulent cucumbers.",
                    "tips": "Provide a trellis for the vines to grow upwards, keeping the fruit off the wet ground to prevent rot.",
                    "benefit": "Excellent for hydration and contains silica for skin and joint health."
                }
            else:
                veg = "Bell Pepper"
                details = {
                    "description": "Bell Peppers are vibrant vegetables that grow best in consistent warmth.",
                    "suitability": f"Your current climate ({temp}°C) provides the steady warmth needed for large, sweet peppers.",
                    "tips": "Peppers need plenty of calcium; use eggshell powder in the soil for better results.",
                    "benefit": "Extremely high in Vitamin A and C for better vision and immunity."
                }
        else:
            # Hot weather crops
            veg = "Ladyfinger (Okra)"
            details = {
                "description": "Okra is a sturdy tropical vegetable that remains productive in high heat.",
                "suitability": f"Your high temperature of {temp}°C would cause many crops to wilt, but Okra thrives in this heat.",
                "tips": "Keep the soil well-aerated and harvest pods daily to encourage new growth.",
                "benefit": "Rich in mucilage, which is excellent for digestive and cardiovascular health."
            }

        VegetableRecommendation.objects.create(
            user=user, temperature=temp, season=season,
            soil_type=soil, recommended_vegetable=veg
        )
        return Response({
            'recommended_vegetable': veg,
            'details': details
        }, status=status.HTTP_201_CREATED)

class ClimateModelingView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        temp = float(request.data.get('temperature'))
        hum = float(request.data.get('humidity'))
        moi = float(request.data.get('soil_moisture'))
        sun = float(request.data.get('sunlight_hours'))
        wind = float(request.data.get('wind_speed'))

        # Backend Validation
        if not (-10 <= temp <= 60) or not (0 <= hum <= 100) or not (0 <= moi <= 100):
            return Response({'detail': 'Unrealistic climate values detected.'}, status=status.HTTP_400_BAD_REQUEST)

        # Climate Risk Advisory mapping
        risks = {
            "Wheat": "Ideal conditions. Ensure the soil remains moist during the tillering stage.",
            "Barley": "Barley is resilient, but watch for excessive humidity which can lead to fungal issues.",
            "Maize": "Heat stress alert! Increase irrigation frequency and consider mulching to retain soil moisture.",
            "Rice": "Perfect Monsoon-like conditions. High Nitrogen uptake expected; monitor leaf color."
        }
        
        # Intelligence Logic to select crop based on climate
        if temp > 28 and hum > 70:
            crop = "Rice"
        elif temp > 25:
            crop = "Maize"
        elif temp <= 22:
            crop = "Wheat"
        else:
            crop = "Barley"

        advice = risks.get(crop, "Monitor climatic variations daily and adapt your irrigation schedule accordingly.")

        MicroClimateModeling.objects.create(
            user=user, temperature=temp, humidity=hum,
            soil_moisture=moi, sunlight_hours=sun, wind_speed=wind,
            predicted_crop=crop
        )
        return Response({
            'predicted_crop': crop,
            'risk_advice': advice
        }, status=status.HTTP_201_CREATED)

class LeafDiseaseView(views.APIView):
    # ── Image Quality Thresholds ──
    MIN_IMAGE_SIZE = 224
    MIN_FILE_SIZE_KB = 10          # Real photos are always > 10KB
    BLUR_THRESHOLD = 100.0         # Laplacian variance
    MIN_UNIQUE_COLORS = 500        # Real photos have thousands; pixel art/clipart < 100

    def _check_image_quality(self, image_path):
        """
        Validates resolution, sharpness, and authenticity of the uploaded image.
        Catches: low-res, blurry, pixel art, clipart, upscaled thumbnails.
        Returns (ok: bool, reason: str | None)
        """
        from PIL import Image as PILImage

        try:
            # 1. File size check
            file_size_kb = os.path.getsize(image_path) / 1024
            if file_size_kb < self.MIN_FILE_SIZE_KB:
                return False, f'Image file is too small ({file_size_kb:.1f}KB). Please upload a real photograph of a leaf.'

            img = PILImage.open(image_path)
            w, h = img.size

            # 2. Resolution check
            if w < self.MIN_IMAGE_SIZE or h < self.MIN_IMAGE_SIZE:
                return False, f'Image resolution too low ({w}×{h}). Please upload an image that is at least {self.MIN_IMAGE_SIZE}×{self.MIN_IMAGE_SIZE} pixels.'

            # Resize to standard analysis size
            img_resized = img.convert('RGB').resize((256, 256))
            arr = np.array(img_resized, dtype=np.uint8)

            # 3. Unique color count — catches pixel art, clipart, upscaled thumbnails
            # Quantize colors into bins of 4 to reduce JPEG noise
            quantized = (arr >> 2).astype(np.uint32)
            color_keys = (quantized[:, :, 0] << 16) | (quantized[:, :, 1] << 8) | quantized[:, :, 2]
            unique_colors = len(np.unique(color_keys))
            if unique_colors < self.MIN_UNIQUE_COLORS:
                return False, 'This image appears to be pixel art, clipart, or a very low-quality image. Please upload a real, high-resolution photograph of a leaf.'

            # 4. Blur detection via Laplacian variance
            grey = np.array(img_resized.convert('L'), dtype=np.float64)
            laplacian = (
                4 * grey[1:-1, 1:-1]
                - grey[:-2, 1:-1]
                - grey[2:, 1:-1]
                - grey[1:-1, :-2]
                - grey[1:-1, 2:]
            )
            variance = np.var(laplacian)
            if variance < self.BLUR_THRESHOLD:
                return False, 'Image appears too blurry. Please upload a clear, focused photo of the leaf.'

            return True, None
        except Exception as e:
            print(f"Image quality check error: {e}")
            return False, 'Could not read or validate the image file.'

    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        image = request.FILES.get('file')
        if not image:
            return Response({'detail': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        disease = "Healthy"
        confidence = 0.95
        
        # Save image temporarily for prediction
        image_path = os.path.join(BASE_DIR, 'temp_leaf_upload.jpg')
        try:
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # --- Image Quality Gate ---
            quality_ok, quality_reason = self._check_image_quality(image_path)
            if not quality_ok:
                return Response({'detail': quality_reason}, status=status.HTTP_400_BAD_REQUEST)
                    
            # Lazy-load the model on first request
            model, metadata = get_leaf_model()
            if model and metadata:
                import predict_leaf_disease
                result, _ = predict_leaf_disease.predict_single_image(model, metadata, image_path)
                disease = result['predicted_class']
                confidence = float(result['confidence']) / 100.0
                treatment = result['disease_info'].get('treatment', 'Consult an expert.')
                prevention = result['disease_info'].get('description', 'Monitor regularly.')
                raw_label = result.get('raw_label', disease)
            else:
                return Response({'detail': 'AI Model not ready.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            print(f"Leaf disease prediction error: {e}")
            return Response({'detail': f'Error processing image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(image_path):
                try: os.remove(image_path)
                except: pass

        # Save to database
        LeafDiseaseDetection.objects.create(
            user=user, image_path=f'leaf_{user.id}_{int(time.time())}.jpg', predicted_disease=disease
        )
        
        return Response({
            'disease': disease,
            'confidence': confidence,
            'treatment': treatment,
            'prevention': prevention
        }, status=status.HTTP_201_CREATED)

class NutritionPredictionView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        temp = float(request.data.get('temperature'))
        hum = float(request.data.get('humidity'))
        ph = float(request.data.get('soil_ph'))
        rain = float(request.data.get('rainfall'))
        moi = float(request.data.get('soil_moisture'))

        # Backend Validation
        if not (-10 <= temp <= 60) or not (0 <= ph <= 14):
            return Response({'detail': 'Unrealistic nutrition parameters detected.'}, status=status.HTTP_400_BAD_REQUEST)

        rec = "High NPK Fertilizer" if rain < 100 else "Standard Compost"
        
        # Nutrition Application Tips
        tips = {
            "High NPK Fertilizer": "The dry conditions require localized application. Apply in a 10cm circle around the plant base.",
            "Standard Compost": "Mix 5-10kg per square meter into the top 15cm of soil before the next rain for best absorption.",
            "Balanced Nutrients": "Use a slow-release granular fertilizer to maintain soil quality throughout the growth cycle."
        }
        
        apply_tips = tips.get(rec, "Apply fertilizer during early morning or late evening to minimize nutrient evaporation.")

        NutritionPrediction.objects.create(
            user=user, temperature=temp, humidity=hum,
            soil_ph=ph, rainfall=rain, soil_moisture=moi,
            nutrition_recommendation=rec
        )
        return Response({
            'nutrition_recommendation': rec,
            'tips': apply_tips
        }, status=status.HTTP_201_CREATED)

class ContactUsView(views.APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        msg = request.data.get('message')

        ContactMessage.objects.create(name=name, email=email, message=msg)
        return Response({'message': 'Message saved'}, status=status.HTTP_201_CREATED)

class AdminDashboardView(views.APIView):
    def get(self, request):
        total_farmers = FarmerProfile.objects.count()
        
        stats = {
            "total_farmers": total_farmers,
            "crop_predictions": CropRecommendation.objects.count(),
            "disease_detections": LeafDiseaseDetection.objects.count(),
            "soil_analysis": SoilTypeIdentification.objects.count(),
            "climate_predictions": MicroClimateModeling.objects.count(),
            "vegetable_recommendations": VegetableRecommendation.objects.count(),
            "nutrition_predictions": NutritionPrediction.objects.count(),
            "contact_messages": ContactMessage.objects.count(),
        }

        # All users with role
        farmers = []
        for u in User.objects.order_by('-date_joined')[:50]:
            role = 'Admin' if hasattr(u, 'admin_profile') else 'Farmer'
            farmers.append({
                "id": u.id,
                "name": u.first_name or u.username,
                "email": u.email,
                "role": role,
                "joined": u.date_joined,
            })

        # Contact messages
        messages = []
        for cm in ContactMessage.objects.order_by('-sent_date')[:20]:
            messages.append({
                "id": cm.id,
                "name": cm.name,
                "email": cm.email,
                "message": cm.message,
                "date": cm.sent_date,
            })

        # Recent activity — merge latest from ALL tables
        activities = []

        for obj in CropRecommendation.objects.select_related('user').order_by('-prediction_date')[:5]:
            activities.append({"user_email": obj.user.email, "feature_used": "Crop Recommendation", "result": obj.recommended_crop, "timestamp": obj.prediction_date, "status": "Completed"})

        for obj in LeafDiseaseDetection.objects.select_related('user').order_by('-detection_date')[:5]:
            activities.append({"user_email": obj.user.email, "feature_used": "Leaf Disease Detection", "result": obj.predicted_disease, "timestamp": obj.detection_date, "status": "Completed"})

        for obj in SoilTypeIdentification.objects.select_related('user').order_by('-analysis_date')[:5]:
            activities.append({"user_email": obj.user.email, "feature_used": "Soil Identification", "result": obj.soil_type_result, "timestamp": obj.analysis_date, "status": "Completed"})

        for obj in MicroClimateModeling.objects.select_related('user').order_by('-prediction_date')[:5]:
            activities.append({"user_email": obj.user.email, "feature_used": "Climate Modeling", "result": obj.predicted_crop, "timestamp": obj.prediction_date, "status": "Completed"})

        for obj in VegetableRecommendation.objects.select_related('user').order_by('-prediction_date')[:5]:
            activities.append({"user_email": obj.user.email, "feature_used": "Vegetable Recommendation", "result": obj.recommended_vegetable, "timestamp": obj.prediction_date, "status": "Completed"})

        for obj in NutritionPrediction.objects.select_related('user').order_by('-prediction_date')[:5]:
            activities.append({"user_email": obj.user.email, "feature_used": "Nutrition Prediction", "result": obj.nutrition_recommendation, "timestamp": obj.prediction_date, "status": "Completed"})

        activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:15]

        return Response({
            "stats": stats,
            "farmers": farmers,
            "messages": messages,
            "recent_activity": activities,
        }, status=status.HTTP_200_OK)

class ManageFarmerView(views.APIView):
    def post(self, request):
        # Create new farmer
        try:
            name = request.data.get('name', '')
            email = request.data.get('email', '')
            password = request.data.get('password', 'Pass123!') # Default if not provided
            
            if User.objects.filter(username=email).exists():
                return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            FarmerProfile.objects.create(user=user, role='farmer')
            return Response({"message": "Farmer created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        # Update farmer
        try:
            user = User.objects.get(pk=pk)
            user.first_name = request.data.get('name', user.first_name)
            user.email = request.data.get('email', user.email)
            user.username = request.data.get('email', user.username)
            user.save()
            return Response({"message": "Farmer updated successfully"})
        except User.DoesNotExist:
            return Response({"error": "Farmer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        # Delete farmer
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({"message": "Farmer deleted successfully"})
        except User.DoesNotExist:
            return Response({"error": "Farmer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def home(request):
    return Response({
        "message": "Smart Agriculture API is Running",
        "version": "1.0.0",
        "endpoints": {
            "register": "/register/",
            "login": "/login/",
            "admin": "/admin/"
        }
    })

