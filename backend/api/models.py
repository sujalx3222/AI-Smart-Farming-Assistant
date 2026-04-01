from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=50, default='admin')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class CropRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_recommendations')
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    soil_ph = models.FloatField()
    rainfall = models.FloatField()
    recommended_crop = models.CharField(max_length=100)
    prediction_date = models.DateTimeField(auto_now_add=True)

class VegetableRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vegetable_recommendations')
    temperature = models.FloatField()
    season = models.CharField(max_length=50)
    soil_type = models.CharField(max_length=100)
    recommended_vegetable = models.CharField(max_length=100)
    prediction_date = models.DateTimeField(auto_now_add=True)

class SoilTypeIdentification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soil_identifications')
    soil_ph = models.FloatField()
    soil_moisture = models.FloatField()
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    soil_type_result = models.CharField(max_length=100)
    analysis_date = models.DateTimeField(auto_now_add=True)

class NutritionPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_predictions')
    temperature = models.FloatField()
    humidity = models.FloatField()
    soil_ph = models.FloatField()
    rainfall = models.FloatField()
    soil_moisture = models.FloatField()
    nutrition_recommendation = models.TextField()
    prediction_date = models.DateTimeField(auto_now_add=True)

class MicroClimateModeling(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='climate_models')
    temperature = models.FloatField()
    humidity = models.FloatField()
    soil_moisture = models.FloatField()
    sunlight_hours = models.FloatField()
    wind_speed = models.FloatField()
    predicted_crop = models.CharField(max_length=100)
    prediction_date = models.DateTimeField(auto_now_add=True)

class LeafDiseaseDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disease_detections')
    image_path = models.CharField(max_length=255)
    predicted_disease = models.CharField(max_length=100)
    detection_date = models.DateTimeField(auto_now_add=True)

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    status = models.CharField(max_length=50, default='pending')
    sent_date = models.DateTimeField(auto_now_add=True)
