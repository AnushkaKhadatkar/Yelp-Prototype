export const selectAuthState = (state) => state.auth

export const selectAuthHydrated = (state) => state.auth.hydrated

export const selectUser = (state) => state.auth.user

export const selectRole = (state) => state.auth.role

export const selectToken = (state) => state.auth.token

export const selectIsLoggedIn = (state) =>
  Boolean(state.auth.user && state.auth.token)

/** Alias for lab wording ("current user"). */
export const selectCurrentUser = (state) => state.auth.user
