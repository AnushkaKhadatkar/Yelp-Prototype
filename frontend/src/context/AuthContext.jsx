import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    const savedRole = localStorage.getItem('role')
    if (savedUser && savedRole) {
      try {
        setUser(JSON.parse(savedUser))
        setRole(savedRole)
      } catch (e) {
        localStorage.clear()
      }
    }
    setLoading(false)
  }, [])

  const login = (userData, userRole, token) => {
    setUser(userData)
    setRole(userRole)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('role', userRole)
  }

  const logout = () => {
    setUser(null)
    setRole(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('role')
  }

  const isOwner = role === 'owner'
  const isUser = role === 'user'

  return (
    <AuthContext.Provider value={{ user, role, login, logout, isOwner, isUser, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
