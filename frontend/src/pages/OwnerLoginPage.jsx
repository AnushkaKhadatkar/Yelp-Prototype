import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { loginOwner, decodeJWT } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function OwnerLoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const res = await loginOwner(form)
      const { access_token, role } = res.data
      const payload = decodeJWT(access_token)
      login({ id: payload.sub, email: form.email, name: form.email.split('@')[0] }, role || 'owner', access_token)
      navigate('/owner/dashboard')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 401) setError(typeof detail === 'string' ? detail : 'Wrong email or password.')
      else if (Array.isArray(detail)) setError(detail.map(d => d.msg).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Login failed.')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 hero-gradient">
      <div className="w-full max-w-md scale-in">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5 justify-center mb-6">
            <div className="w-12 h-12 bg-[#E8321A] rounded-2xl flex items-center justify-center shadow-red">
              <span className="font-display text-white font-bold text-2xl italic">y</span>
            </div>
          </Link>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[rgba(253,248,243,0.15)] mb-4">
            <span style={{ fontSize: 11, color: 'rgba(253,248,243,0.6)', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Owner Portal
            </span>
          </div>
          <h1 className="font-display text-3xl text-white font-semibold">Owner Login</h1>
          <p style={{ color: 'rgba(253,248,243,0.5)', marginTop: 4 }}>Manage your restaurant</p>
        </div>

        <div className="rounded-2xl p-8" style={{ background: 'rgba(253,248,243,0.05)', border: '1px solid rgba(253,248,243,0.1)', backdropFilter: 'blur(20px)' }}>
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { name: 'email', label: 'Email address', type: 'email' },
              { name: 'password', label: 'Password', type: 'password' },
            ].map(f => (
              <div key={f.name}>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'rgba(253,248,243,0.5)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                  {f.label}
                </label>
                <input type={f.type} value={form[f.name]}
                  onChange={e => setForm({...form, [f.name]: e.target.value})}
                  required
                  style={{
                    width: '100%', padding: '12px 16px',
                    background: 'rgba(253,248,243,0.08)',
                    border: '1px solid rgba(253,248,243,0.15)',
                    borderRadius: 12, fontSize: 14,
                    color: 'white', outline: 'none',
                    fontFamily: "'Outfit', sans-serif",
                  }}
                  className="placeholder-[rgba(253,248,243,0.3)]"
                  placeholder={f.type === 'email' ? 'owner@restaurant.com' : '••••••••'}
                />
              </div>
            ))}

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl"
                style={{ background: 'rgba(232,50,26,0.2)', border: '1px solid rgba(232,50,26,0.3)' }}>
                <p style={{ fontSize: 13, color: '#FCA5A5' }}>{error}</p>
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3.5 rounded-xl text-base">
              {loading ? 'Signing in...' : 'Sign In as Owner'}
            </button>
          </form>

          <div style={{ height: 1, background: 'rgba(253,248,243,0.1)', margin: '20px 0' }} />
          <p style={{ fontSize: 14, color: 'rgba(253,248,243,0.4)', textAlign: 'center' }}>
            New owner?{' '}
            <Link to="/owner/signup" style={{ color: '#E8321A', fontWeight: 600 }} className="hover:underline">Register here</Link>
          </p>
          <p style={{ fontSize: 13, color: 'rgba(253,248,243,0.3)', textAlign: 'center', marginTop: 10 }}>
            <Link to="/login" style={{ color: 'rgba(253,248,243,0.4)' }} className="hover:text-white transition-colors">← Regular user login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
