export const selectRestaurantState = (state) => state.restaurant

export const selectRestaurantList = (state) => state.restaurant.list

export const selectRestaurantLoading = (state) => state.restaurant.loading

export const selectRestaurantError = (state) => state.restaurant.error

export const selectRestaurantFilters = (state) => state.restaurant.filters

export const selectRestaurantActiveFilter = (state) => state.restaurant.activeFilter

export const selectSelectedRestaurant = (state) => state.restaurant.selectedRestaurant
