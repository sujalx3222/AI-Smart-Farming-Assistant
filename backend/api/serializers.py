from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class FarmerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = FarmerProfile
        fields = ['user', 'phone', 'location', 'created_at']

class CropRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropRecommendation
        fields = '__all__'

class VegetableRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VegetableRecommendation
        fields = '__all__'

class SoilTypeIdentificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilTypeIdentification
        fields = '__all__'

class NutritionPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionPrediction
        fields = '__all__'

class MicroClimateModelingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroClimateModeling
        fields = '__all__'

class LeafDiseaseDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeafDiseaseDetection
        fields = '__all__'

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
