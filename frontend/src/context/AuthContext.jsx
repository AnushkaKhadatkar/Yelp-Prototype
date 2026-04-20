import { useEffect, useCallback, useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { hydrateAuth, setCredentials, logout as logoutAction } from '../slices/authSlice'
import {
  selectAuthHydrated,
  selectUser,
  selectRole,
} from '../selectors/authSelectors'

/** Hydrate JWT + user from localStorage once; keeps axios interceptors and Redux in sync. */
export function AuthBootstrap({ children }) {
  const dispatch = useDispatch()
  useEffect(() => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    const role = localStorage.getItem('role')
    if (token && userStr && role) {
      try {
        dispatch(hydrateAuth({ token, user: JSON.parse(userStr), role }))
      } catch {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('role')
        dispatch(hydrateAuth(null))
      }
    } else {
      dispatch(hydrateAuth(null))
    }
  }, [dispatch])
  return children
}

export function useAuth() {
  const dispatch = useDispatch()
  const hydrated = useSelector(selectAuthHydrated)
  const user = useSelector(selectUser)
  const role = useSelector(selectRole)

  const login = useCallback(
    (userData, userRole, token) => {
      dispatch(setCredentials({ user: userData, role: userRole, token }))
    },
    [dispatch]
  )

  const logout = useCallback(() => {
    dispatch(logoutAction())
  }, [dispatch])

  return useMemo(
    () => ({
      user,
      role,
      login,
      logout,
      loading: !hydrated,
      isOwner: role === 'owner',
      isUser: role === 'user',
    }),
    [user, role, login, logout, hydrated]
  )
}
