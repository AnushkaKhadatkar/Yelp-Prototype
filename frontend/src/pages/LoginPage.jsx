import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { loginUser, decodeJWT } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const res = await loginUser(form)
<<<<<<< HEAD
      const { access_token, role } = res.data
      const payload = decodeJWT(access_token)
      login({ id: payload.sub, email: form.email, name: form.email.split('@')[0] }, role || 'user', access_token)
=======
      const { role } = res.data
      const token = res.data.access_token || res.data.token
      const payload = decodeJWT(token)
      login({ id: payload.sub, email: form.email, name: form.email.split('@')[0] }, role || 'user', token)
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea
      navigate('/')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 401) setError('Wrong email or password.')
      else if (Array.isArray(detail)) setError(detail.map(d => d.msg).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Login failed.')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--cream)' }}>
      {/* Left panel */}
      <div className="hidden lg:flex w-1/2 hero-gradient flex-col items-center justify-center p-16 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full opacity-5" style={{ background: 'var(--red)' }} />
        <div className="absolute -bottom-20 -left-20 w-64 h-64 rounded-full opacity-5" style={{ background: 'var(--gold)' }} />
        <div className="relative text-center">
          <div className="w-16 h-16 bg-[#E8321A] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-red">
            <span className="font-display text-white font-bold text-3xl italic">y</span>
          </div>
          <h2 className="font-display text-4xl text-white font-semibold mb-4 leading-tight">
            Find your next<br />
            <em className="text-[#E8321A]">favorite restaurant</em>
          </h2>
          <p className="text-[rgba(253,248,243,0.5)] text-lg max-w-sm">
            Discover great places, write reviews, and let AI guide your next meal.
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md scale-in">
          <div className="lg:hidden flex items-center gap-2.5 mb-8">
            <div className="w-10 h-10 bg-[#E8321A] rounded-xl flex items-center justify-center">
              <span className="font-display text-white font-bold text-xl italic">y</span>
            </div>
            <span className="font-display text-2xl font-semibold">yelp<span className="text-[#E8321A]">.</span></span>
          </div>

          <h1 className="font-display text-3xl font-semibold text-[#1A1208] mb-1">Welcome back</h1>
          <p className="text-[#8C7E6E] mb-8">Sign in to your account</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="float-wrap">
              <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                placeholder=" " required className="float-input" id="email" />
              <label htmlFor="email" className="float-label">Email address</label>
            </div>
            <div className="float-wrap">
              <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})}
                placeholder=" " required className="float-input" id="password" />
              <label htmlFor="password" className="float-label">Password</label>
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl"
                style={{ background: 'rgba(232,50,26,0.08)', border: '1px solid rgba(232,50,26,0.2)' }}>
                <span style={{ fontSize: 14, color: 'var(--red)' }}>⚠</span>
                <p style={{ fontSize: 13, color: 'var(--red)' }}>{error}</p>
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3.5 rounded-xl text-base">
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="divider" />
          <p style={{ fontSize: 14, color: 'var(--muted)', textAlign: 'center' }}>
            New to Yelp?{' '}
            <Link to="/signup" style={{ color: 'var(--red)', fontWeight: 600 }} className="hover:underline">Create account</Link>
          </p>
          <p style={{ fontSize: 13, color: 'var(--muted)', textAlign: 'center', marginTop: 12 }}>
            Restaurant owner?{' '}
            <Link to="/owner/login" style={{ color: 'var(--ink)', fontWeight: 500 }} className="hover:text-[var(--red)] transition-colors">Owner login →</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
