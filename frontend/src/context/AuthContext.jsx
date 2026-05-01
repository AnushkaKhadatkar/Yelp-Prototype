import { useEffect, useCallback, useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { hydrateAuth, setCredentials, logout as logoutAction } from '../slices/authSlice'
import { getOwnerProfile, getUserProfile } from '../services/api'
import {
  selectAuthHydrated,
  selectUser,
  selectRole,
} from '../selectors/authSelectors'

/** Hydrate JWT + user from localStorage once; keeps axios interceptors and Redux in sync. */
export function AuthBootstrap({ children }) {
  const dispatch = useDispatch()
  useEffect(() => {
    const refreshUserFromBackend = async (token, user, role) => {
      try {
        const res = role === 'owner' ? await getOwnerProfile() : await getUserProfile()
        const d = res?.data || {}
        const mergedUser =
          role === 'owner'
            ? {
                ...user,
                id: d.id ?? user?.id,
                name: d.name || user?.name,
                email: d.email || user?.email,
                profile_pic: d.profile_pic ?? user?.profile_pic ?? null,
              }
            : {
                ...user,
                id: d.id ?? user?.id,
                name: d.name || user?.name,
                email: d.email || user?.email,
                profile_pic: d.profile_pic ?? user?.profile_pic ?? null,
              }
        dispatch(setCredentials({ user: mergedUser, role, token }))
      } catch {
        // Ignore refresh failures; keep hydrated local session.
      }
    }

    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    const role = localStorage.getItem('role')
    if (token && userStr && role) {
      try {
        const user = JSON.parse(userStr)
        dispatch(hydrateAuth({ token, user, role }))
        refreshUserFromBackend(token, user, role)
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
