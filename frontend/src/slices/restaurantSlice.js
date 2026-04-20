import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { getRestaurants } from '../services/api'

const emptyFilters = () => ({
  search: '',
  city: '',
  keyword: '',
  cuisine: '',
})

export const fetchRestaurants = createAsyncThunk(
  'restaurant/fetchRestaurants',
  async (paramsOverride, { getState, rejectWithValue }) => {
    const filters = getState().restaurant.filters
    const merged = { ...filters, ...(paramsOverride || {}) }
    const params = {}
    if (merged.search) params.search = merged.search
    if (merged.city) params.city = merged.city
    if (merged.keyword) params.keyword = merged.keyword
    if (merged.cuisine) params.cuisine = merged.cuisine
    try {
      const res = await getRestaurants(params)
      return res.data
    } catch {
      return rejectWithValue('Could not connect to the server.')
    }
  }
)

const initialState = {
  list: [],
  loading: false,
  error: null,
  filters: emptyFilters(),
  activeFilter: 'All',
  selectedRestaurant: null,
}

export const restaurantSlice = createSlice({
  name: 'restaurant',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload }
    },
    setActiveFilter: (state, action) => {
      state.activeFilter = action.payload
    },
    setSelectedRestaurant: (state, action) => {
      state.selectedRestaurant = action.payload
    },
    clearFilters: (state) => {
      state.filters = emptyFilters()
      state.activeFilter = 'All'
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRestaurants.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchRestaurants.fulfilled, (state, action) => {
        state.loading = false
        const body = action.payload
        state.list = Array.isArray(body?.restaurants)
          ? body.restaurants
          : Array.isArray(body)
            ? body
            : []
      })
      .addCase(fetchRestaurants.rejected, (state, action) => {
        state.loading = false
        state.error = typeof action.payload === 'string' ? action.payload : 'Request failed.'
      })
  },
})

export const { setFilters, setActiveFilter, setSelectedRestaurant, clearFilters } =
  restaurantSlice.actions
export default restaurantSlice.reducer
