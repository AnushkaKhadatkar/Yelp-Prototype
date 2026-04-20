import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  token: null,
  user: null,
  role: null,
  hydrated: false,
}

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setToken: (state, action) => {
      const token = action.payload
      state.token = token
      if (token) localStorage.setItem('token', token)
      else localStorage.removeItem('token')
    },
    setCredentials: (state, action) => {
      const { user, role, token } = action.payload
      state.user = user
      state.role = role
      state.token = token
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('role', role)
    },
    logout: (state) => {
      state.user = null
      state.role = null
      state.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
    },
    /** Called once on app load (from localStorage or empty session). */
    hydrateAuth: (state, action) => {
      const p = action.payload
      if (p?.token && p?.user && p?.role) {
        state.token = p.token
        state.user = p.user
        state.role = p.role
      } else {
        state.token = null
        state.user = null
        state.role = null
      }
      state.hydrated = true
    },
  },
})

export const { setToken, setCredentials, logout, hydrateAuth } = authSlice.actions
export default authSlice.reducer
