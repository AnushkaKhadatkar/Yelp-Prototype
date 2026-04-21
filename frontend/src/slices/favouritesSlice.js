import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { addFavourite, getFavourites, removeFavourite } from '../services/api'

const normalizeRestaurant = (r) => ({
  ...r,
  id: Number(r?.id ?? r?.restaurant_id),
})

export const fetchFavourites = createAsyncThunk(
  'favourites/fetchFavourites',
  async (_, { rejectWithValue }) => {
    try {
      const res = await getFavourites()
      const list = Array.isArray(res?.data) ? res.data : []
      return list.map(normalizeRestaurant).filter((r) => Number.isFinite(r.id))
    } catch {
      return rejectWithValue('Failed to load favourites.')
    }
  }
)

export const addFavouriteItem = createAsyncThunk(
  'favourites/addFavouriteItem',
  async (restaurantId, { rejectWithValue }) => {
    try {
      await addFavourite(restaurantId)
      return Number(restaurantId)
    } catch {
      return rejectWithValue('Failed to add favourite.')
    }
  }
)

export const removeFavouriteItem = createAsyncThunk(
  'favourites/removeFavouriteItem',
  async (restaurantId, { rejectWithValue }) => {
    try {
      await removeFavourite(restaurantId)
      return Number(restaurantId)
    } catch {
      return rejectWithValue('Failed to remove favourite.')
    }
  }
)

const initialState = {
  items: [],
  ids: [],
  loading: false,
  error: null,
  pendingById: {},
}

export const favouritesSlice = createSlice({
  name: 'favourites',
  initialState,
  reducers: {
    optimisticAddFavourite: (state, action) => {
      const id = Number(action.payload)
      if (!state.ids.includes(id)) state.ids.push(id)
    },
    optimisticRemoveFavourite: (state, action) => {
      const id = Number(action.payload)
      state.ids = state.ids.filter((x) => x !== id)
      state.items = state.items.filter((x) => x.id !== id)
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFavourites.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchFavourites.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
        state.ids = action.payload.map((r) => r.id)
      })
      .addCase(fetchFavourites.rejected, (state, action) => {
        state.loading = false
        state.error =
          typeof action.payload === 'string' ? action.payload : 'Failed to load favourites.'
      })
      .addCase(addFavouriteItem.pending, (state, action) => {
        const id = Number(action.meta.arg)
        state.pendingById[id] = true
      })
      .addCase(addFavouriteItem.fulfilled, (state, action) => {
        const id = action.payload
        if (!state.ids.includes(id)) state.ids.push(id)
        delete state.pendingById[id]
      })
      .addCase(addFavouriteItem.rejected, (state, action) => {
        const id = Number(action.meta.arg)
        state.ids = state.ids.filter((x) => x !== id)
        delete state.pendingById[id]
        state.error =
          typeof action.payload === 'string' ? action.payload : 'Failed to add favourite.'
      })
      .addCase(removeFavouriteItem.pending, (state, action) => {
        const id = Number(action.meta.arg)
        state.pendingById[id] = true
      })
      .addCase(removeFavouriteItem.fulfilled, (state, action) => {
        const id = action.payload
        state.ids = state.ids.filter((x) => x !== id)
        state.items = state.items.filter((x) => x.id !== id)
        delete state.pendingById[id]
      })
      .addCase(removeFavouriteItem.rejected, (state, action) => {
        const id = Number(action.meta.arg)
        if (!state.ids.includes(id)) state.ids.push(id)
        delete state.pendingById[id]
        state.error =
          typeof action.payload === 'string' ? action.payload : 'Failed to remove favourite.'
      })
  },
})

export const { optimisticAddFavourite, optimisticRemoveFavourite } = favouritesSlice.actions
export default favouritesSlice.reducer
