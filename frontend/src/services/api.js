import axios from 'axios'
import { logout } from '../slices/authSlice'
import { getStore } from '../storeRef'

// Same-origin by default: Vite (dev) and nginx (Docker) proxy to microservices.
// Set VITE_API_BASE_URL only when the API is on another origin.
const baseURL = import.meta.env.VITE_API_BASE_URL ?? ''

const API = axios.create({
  baseURL,
})

API.interceptors.request.use((req) => {
  const token = localStorage.getItem('token')
  if (token) req.headers.Authorization = `Bearer ${token}`
  return req
})

API.interceptors.response.use(
  (res) => res,
  (err) => {
    const isAuthRoute = err.config?.url?.includes('/auth/')
    if (err.response?.status === 401 && !isAuthRoute) {
      getStore()?.dispatch(logout())
    }
    return Promise.reject(err)
  }
)

// Helper: decode JWT payload without a library
export const decodeJWT = (token) => {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return {}
  }
}

// AUTH — correct routes from auth_user.py (prefix /auth/user) and auth_owner.py (prefix /auth/owner)
export const signupUser  = (data) => API.post('/auth/user/signup',  data)
export const loginUser   = (data) => API.post('/auth/user/login',   data)
export const signupOwner = (data) => API.post('/auth/owner/signup', data)
export const loginOwner  = (data) => API.post('/auth/owner/login',  data)
export const logoutUser  = () => Promise.resolve()

// USER PROFILE
export const getUserProfile      = ()     => API.get('/users/profile')
export const updateUserProfile   = (data) => API.put('/users/profile', data)
export const uploadProfilePicture = (formData) =>
  API.post('/users/profile/picture', formData, { headers: { 'Content-Type': 'multipart/form-data' } })

// USER PREFERENCES
export const getUserPreferences    = ()     => API.get('/users/preferences')
export const updateUserPreferences = (data) => API.put('/users/preferences', data)

// RESTAURANTS
export const getRestaurants    = (params) => API.get('/restaurants', { params })
export const getRestaurantById = (id)     => API.get(`/restaurants/${id}`)
export const createRestaurant  = (data)   => API.post('/restaurants', data, { headers: { 'Content-Type': 'multipart/form-data' } })
export const updateRestaurant  = (id, data) => API.put(`/restaurants/${id}`, data)
export const deleteRestaurant  = (id)     => API.delete(`/restaurants/${id}`)

// REVIEWS
export const getReviews    = (restaurantId)       => API.get(`/restaurants/${restaurantId}/reviews`)
export const createReview  = (restaurantId, data) => API.post(`/restaurants/${restaurantId}/reviews`, data)
export const updateReview  = (reviewId, data)     => API.put(`/reviews/${reviewId}`, data)
export const deleteReview  = (reviewId)           => API.delete(`/reviews/${reviewId}`)
export const uploadReviewPhotos = (reviewId, formData) =>
  API.post(`/reviews/${reviewId}/photos`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })

// FAVOURITES
export const getFavourites    = ()             => API.get('/users/favourites')
export const addFavourite     = (restaurantId) => API.post(`/users/favourites/${restaurantId}`)
export const removeFavourite  = (restaurantId) => API.delete(`/users/favourites/${restaurantId}`)

// HISTORY
export const getHistory = () => API.get('/users/history')

// OWNER
export const getOwnerProfile          = ()       => API.get('/owner/profile')
export const updateOwnerProfile       = (data)   => API.put('/owner/profile', data)
export const uploadOwnerProfilePicture = (formData) =>
  API.post('/owner/profile/picture', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
export const createOwnerRestaurant    = (data)   => API.post('/owner/restaurants', data)
export const claimRestaurant          = (id)     => API.post(`/owner/restaurants/${id}/claim`)
export const getOwnerDashboard        = ()       => API.get('/owner/dashboard')
export const getOwnerRestaurantReviews = (id)    => API.get(`/owner/restaurants/${id}/reviews`)

// AI ASSISTANT
export const chatWithAI = (data) => API.post('/ai-assistant/chat', data)

export default API
