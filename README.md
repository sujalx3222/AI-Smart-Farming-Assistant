# AI Smart Farming Assistant 🌾

An AI-powered agricultural advisory system designed to help farmers optimize crop yields, identify soil conditions, and detect leaf diseases. This project integrates machine learning models with a modern full-stack web application.

## 🚀 Features

- **Crop Recommendation**: Predicts the best crop to grow base on environmental factors (N, P, K, pH, etc.).
- **Leaf Disease Detection**: Analyzes leaf images to identify potential diseases using CNN models.
- **Soil Identification**: Identifies soil types to recommend appropriate farming practices.
- **Vegetable Engine**: Specialized recommendations for vegetable farming.
- **Climate Modeling**: Insights into weather patterns for better planning.
- **Admin Dashboard**: Comprehensive statistics and farmer management for agricultural officers.

## 🛠️ Technology Stack

- **Backend**: Django & Django REST Framework
- **Frontend**: React (Vite)
- **AI/ML**: Scikit-Learn, NumPy, Pandas, Joblib (TensorFlow compatible)
- **Styling**: Premium Modern CSS

## 📋 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm

### Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sujalx3222/AI-Smart-Farming-Assistant
   cd AI-Smart-Farming-Assistant
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

## 📂 Project Structure

- `backend/`: Django core, API endpoints, and Machine Learning logic.
- `frontend/`: React components, pages, and UI/UX design.

## 📄 License

This project is licensed under the MIT License.
