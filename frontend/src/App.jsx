import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import CropRecommendation from './pages/CropRecommendation';
import SoilIdentification from './pages/SoilIdentification';
import VegetableRecommendation from './pages/VegetableRecommendation';
import ClimateModeling from './pages/ClimateModeling';
import LeafDisease from './pages/LeafDisease';
import NutritionPrediction from './pages/NutritionPrediction';
import Contact from './pages/Contact';
import AdminDashboard from './pages/AdminDashboard';
import AboutUs from './pages/AboutUs';
import './pages/Auth.css';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes — must be logged in */}
        <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/crop" element={<ProtectedRoute><CropRecommendation /></ProtectedRoute>} />
        <Route path="/soil" element={<ProtectedRoute><SoilIdentification /></ProtectedRoute>} />
        <Route path="/vegetable" element={<ProtectedRoute><VegetableRecommendation /></ProtectedRoute>} />
        <Route path="/climate" element={<ProtectedRoute><ClimateModeling /></ProtectedRoute>} />
        <Route path="/leaf-disease" element={<ProtectedRoute><LeafDisease /></ProtectedRoute>} />
        <Route path="/nutrition" element={<ProtectedRoute><NutritionPrediction /></ProtectedRoute>} />
        <Route path="/contact" element={<ProtectedRoute><Contact /></ProtectedRoute>} />
        <Route path="/about" element={<ProtectedRoute><AboutUs /></ProtectedRoute>} />

        {/* Admin Only Route */}
        <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}

export default App;
