from django.urls import path
from .views import *
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('recommend_crop/', CropRecommendationView.as_view(), name='recommend_crop'),
    path('identify_soil/', SoilIdentificationView.as_view(), name='identify_soil'),
    path('vegetable_recommendation/', VegetableRecommendationView.as_view(), name='vegetable_recommendation'),
    path('climate_modeling/', ClimateModelingView.as_view(), name='climate_modeling'),
    path('detect_disease/', LeafDiseaseView.as_view(), name='detect_disease'),
    path('predict_nutrition/', NutritionPredictionView.as_view(), name='predict_nutrition'),
    path('contact_us/', ContactUsView.as_view(), name='contact_us'),
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='dashboard_stats'),
    path('api/farmers/', ManageFarmerView.as_view(), name='create_farmer'),
    path('api/farmers/<int:pk>/', ManageFarmerView.as_view(), name='manage_farmer'),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
