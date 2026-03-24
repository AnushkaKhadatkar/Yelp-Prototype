import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { logoutUser } from '../services/api'

export default function Navbar() {
  const { user, role, logout, isOwner } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleLogout = async () => {
    try { await logoutUser() } catch {}
    logout()
    navigate('/')
    setMenuOpen(false)
  }

  const isActive = (path) => location.pathname === path

  const navLink = (to, label) => (
    <Link to={to}
      className={`relative px-1 py-2 text-sm font-medium transition-colors duration-200 ${
        isActive(to)
          ? 'text-[#E8321A]'
          : 'text-[#3D3426] hover:text-[#1A1208]'
      }`}
      onClick={() => setMenuOpen(false)}
    >
      {label}
      {isActive(to) && (
        <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#E8321A] rounded-full" />
      )}
    </Link>
  )

  return (
    <nav className={`sticky top-0 z-50 transition-all duration-300 ${
      scrolled
        ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-[rgba(26,18,8,0.06)]'
        : 'bg-[#FDF8F3] border-b border-[rgba(26,18,8,0.06)]'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 bg-[#E8321A] rounded-xl flex items-center justify-center shadow-sm group-hover:shadow-red transition-all duration-200">
              <span className="font-display text-white font-bold text-lg italic">y</span>
            </div>
            <span className="font-display text-[#1A1208] font-semibold text-xl tracking-tight">
              yelp<span className="text-[#E8321A]">.</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            {navLink('/', 'Explore')}
            {user && !isOwner && (<>
              {navLink('/favourites', '♥ Saved')}
              {navLink('/history', 'History')}
              {navLink('/add-restaurant', '+ Add')}
            </>)}
            {isOwner && (<>
              {navLink('/owner/dashboard', 'Dashboard')}
              {navLink('/owner/restaurant', 'My Restaurant')}
              {navLink('/owner/reviews', 'Reviews')}
            </>)}
          </div>

          {/* Auth */}
          <div className="hidden md:flex items-center gap-2">
            {!user ? (
              <>
                <Link to="/login" className="btn-ghost text-sm px-4 py-2">Log In</Link>
                <Link to="/signup" className="btn-primary text-sm px-5 py-2">Sign Up</Link>
                <Link to="/owner/login"
                  className="text-sm font-medium text-[#8C7E6E] hover:text-[#E8321A] transition-colors px-2">
                  Owner
                </Link>
              </>
            ) : (
              <div className="flex items-center gap-3">
                {!isOwner && (
                  <Link to="/profile"
                    className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl hover:bg-[rgba(26,18,8,0.04)] transition-colors">
                    <div className="w-8 h-8 bg-[#E8321A] rounded-full flex items-center justify-center shadow-sm">
                      <span className="text-white font-semibold text-xs">
                        {user.name?.[0]?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-[#3D3426]">{user.name}</span>
                  </Link>
                )}
                {isOwner && (
                  <div className="flex items-center gap-2 px-3 py-1.5">
                    <div className="w-8 h-8 bg-[#1A1208] rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold text-xs">{user.name?.[0]?.toUpperCase()}</span>
                    </div>
                    <span className="text-sm font-medium text-[#3D3426]">{user.name}</span>
                  </div>
                )}
                <button onClick={handleLogout}
                  className="text-sm text-[#8C7E6E] hover:text-[#E8321A] transition-colors font-medium px-2">
                  Log Out
                </button>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button className="md:hidden p-2 rounded-lg hover:bg-[rgba(26,18,8,0.04)]"
            onClick={() => setMenuOpen(!menuOpen)}>
            <div className="w-5 flex flex-col gap-1.5">
              <span className={`block h-0.5 bg-[#1A1208] rounded transition-all ${menuOpen ? 'rotate-45 translate-y-2' : ''}`} />
              <span className={`block h-0.5 bg-[#1A1208] rounded transition-all ${menuOpen ? 'opacity-0' : ''}`} />
              <span className={`block h-0.5 bg-[#1A1208] rounded transition-all ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
            </div>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 pt-2 border-t border-[rgba(26,18,8,0.06)] space-y-0.5 fade-in">
            <MobileLink to="/" label="Explore" onClick={() => setMenuOpen(false)} active={isActive('/')} />
            {user && !isOwner && (<>
              <MobileLink to="/favourites" label="♥ Saved" onClick={() => setMenuOpen(false)} active={isActive('/favourites')} />
              <MobileLink to="/history" label="History" onClick={() => setMenuOpen(false)} active={isActive('/history')} />
              <MobileLink to="/add-restaurant" label="+ Add Restaurant" onClick={() => setMenuOpen(false)} active={isActive('/add-restaurant')} />
              <MobileLink to="/profile" label="Profile" onClick={() => setMenuOpen(false)} active={isActive('/profile')} />
            </>)}
            {isOwner && (<>
              <MobileLink to="/owner/dashboard" label="Dashboard" onClick={() => setMenuOpen(false)} active={isActive('/owner/dashboard')} />
              <MobileLink to="/owner/restaurant" label="My Restaurant" onClick={() => setMenuOpen(false)} active={isActive('/owner/restaurant')} />
              <MobileLink to="/owner/reviews" label="Reviews" onClick={() => setMenuOpen(false)} active={isActive('/owner/reviews')} />
            </>)}
            {!user ? (<>
              <MobileLink to="/login" label="Log In" onClick={() => setMenuOpen(false)} active={false} />
              <div className="px-3 pt-2">
                <Link to="/signup" className="btn-primary w-full justify-center" onClick={() => setMenuOpen(false)}>Sign Up</Link>
              </div>
            </>) : (
              <button onClick={handleLogout}
                className="w-full text-left px-3 py-2.5 text-sm font-medium text-[#E8321A] hover:bg-red-50 rounded-xl transition-colors">
                Log Out
              </button>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}

function MobileLink({ to, label, onClick, active }) {
  return (
    <Link to={to} onClick={onClick}
      className={`block px-3 py-2.5 text-sm font-medium rounded-xl transition-colors ${
        active ? 'bg-red-50 text-[#E8321A]' : 'text-[#3D3426] hover:bg-[rgba(26,18,8,0.04)]'
      }`}>
      {label}
    </Link>
  )
}
