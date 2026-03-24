import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import OwnerLoginPage from './pages/OwnerLoginPage'
import OwnerSignupPage from './pages/OwnerSignupPage'
import RestaurantDetailsPage from './pages/RestaurantDetailsPage'
import ProfilePage from './pages/ProfilePage'
import AddRestaurantPage from './pages/AddRestaurantPage'
import FavouritesPage from './pages/FavouritesPage'
import HistoryPage from './pages/HistoryPage'
import OwnerDashboardPage from './pages/OwnerDashboardPage'
import OwnerRestaurantPage from './pages/OwnerRestaurantPage'
import OwnerReviewsPage from './pages/OwnerReviewsPage'

function ProtectedRoute({ children, requireRole }) {
  const { user, role, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-10 w-10 border-4 border-red-600 border-t-transparent" /></div>
  if (!user) return <Navigate to="/login" replace />
  if (requireRole && role !== requireRole) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Routes>
        {/* Public */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/owner/login" element={<OwnerLoginPage />} />
        <Route path="/owner/signup" element={<OwnerSignupPage />} />
        <Route path="/restaurants/:id" element={<RestaurantDetailsPage />} />

        {/* User Protected */}
        <Route path="/profile" element={<ProtectedRoute requireRole="user"><ProfilePage /></ProtectedRoute>} />
        <Route path="/add-restaurant" element={<ProtectedRoute requireRole="user"><AddRestaurantPage /></ProtectedRoute>} />
        <Route path="/favourites" element={<ProtectedRoute requireRole="user"><FavouritesPage /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute requireRole="user"><HistoryPage /></ProtectedRoute>} />

        {/* Owner Protected */}
        <Route path="/owner/dashboard" element={<ProtectedRoute requireRole="owner"><OwnerDashboardPage /></ProtectedRoute>} />
        <Route path="/owner/restaurant" element={<ProtectedRoute requireRole="owner"><OwnerRestaurantPage /></ProtectedRoute>} />
        <Route path="/owner/reviews" element={<ProtectedRoute requireRole="owner"><OwnerReviewsPage /></ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
