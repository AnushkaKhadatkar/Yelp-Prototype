import { configureStore } from '@reduxjs/toolkit'

import authReducer from '../slices/authSlice'
import restaurantReducer from '../slices/restaurantSlice'
import reviewReducer from '../slices/reviewSlice'
import favouritesReducer from '../slices/favouritesSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    restaurant: restaurantReducer,
    review: reviewReducer,
    favourites: favouritesReducer,
  },
})
