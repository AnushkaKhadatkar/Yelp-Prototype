import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signupOwner, loginOwner, decodeJWT } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function OwnerSignupPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '', restaurant_location: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    if (form.password !== form.confirm) { setError("Passwords don't match."); return }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setLoading(true)
    try {
      await signupOwner({ name: form.name, email: form.email, password: form.password, restaurant_location: form.restaurant_location })
      const res = await loginOwner({ email: form.email, password: form.password })
      const { role } = res.data
      const token = res.data.access_token || res.data.token
      const payload = decodeJWT(token)
      login({ id: payload.sub, email: form.email, name: form.name }, role || 'owner', token)
      navigate('/owner/dashboard')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 400) setError('An account with this email already exists.')
      else if (Array.isArray(detail)) setError(detail.map(d => d.msg).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Signup failed.')
    }
    setLoading(false)
  }

  const fields = [
    { name: 'name', label: 'Full name', type: 'text', placeholder: 'Jane Smith' },
    { name: 'email', label: 'Email address', type: 'email', placeholder: 'jane@myrestaurant.com' },
    { name: 'restaurant_location', label: 'Restaurant city / location', type: 'text', placeholder: 'San Jose, CA' },
    { name: 'password', label: 'Password', type: 'password', placeholder: '••••••••' },
    { name: 'confirm', label: 'Confirm password', type: 'password', placeholder: '••••••••' },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-6 hero-gradient overflow-y-auto">
      <div className="w-full max-w-md py-8 scale-in">
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
          <h1 className="font-display text-3xl text-white font-semibold">Register as Owner</h1>
          <p style={{ color: 'rgba(253,248,243,0.5)', marginTop: 4 }}>Get your restaurant listed today</p>
        </div>

        <div className="rounded-2xl p-8" style={{ background: 'rgba(253,248,243,0.05)', border: '1px solid rgba(253,248,243,0.1)', backdropFilter: 'blur(20px)' }}>
          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map(f => (
              <div key={f.name}>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'rgba(253,248,243,0.5)', letterSpacing: '0.08em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                  {f.label}
                </label>
                <input type={f.type} value={form[f.name]}
                  onChange={e => setForm({...form, [f.name]: e.target.value})}
                  required placeholder={f.placeholder}
                  style={{
                    width: '100%', padding: '12px 16px',
                    background: 'rgba(253,248,243,0.08)',
                    border: '1px solid rgba(253,248,243,0.15)',
                    borderRadius: 12, fontSize: 14,
                    color: 'white', outline: 'none',
                    fontFamily: "'Outfit', sans-serif",
                  }}
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
              {loading ? 'Creating account...' : 'Register as Owner'}
            </button>
          </form>

          <div style={{ height: 1, background: 'rgba(253,248,243,0.1)', margin: '20px 0' }} />
          <p style={{ fontSize: 14, color: 'rgba(253,248,243,0.4)', textAlign: 'center' }}>
            Already registered?{' '}
            <Link to="/owner/login" style={{ color: '#E8321A', fontWeight: 600 }} className="hover:underline">Owner login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
