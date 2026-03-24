import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signupUser, loginUser, decodeJWT } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function SignupPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
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
      await signupUser({ name: form.name, email: form.email, password: form.password })
      const res = await loginUser({ email: form.email, password: form.password })
      const { access_token, role } = res.data
      const payload = decodeJWT(access_token)
      login({ id: payload.sub, email: form.email, name: form.name }, role || 'user', access_token)
      navigate('/')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 400) setError('An account with this email already exists.')
      else if (Array.isArray(detail)) setError(detail.map(d => d.msg).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Signup failed.')
    }
    setLoading(false)
  }

  const fields = [
    { name: 'name', label: 'Full name', type: 'text' },
    { name: 'email', label: 'Email address', type: 'email' },
    { name: 'password', label: 'Password', type: 'password' },
    { name: 'confirm', label: 'Confirm password', type: 'password' },
  ]

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--cream)' }}>
      <div className="hidden lg:flex w-1/2 hero-gradient flex-col items-center justify-center p-16 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full opacity-5" style={{ background: 'var(--red)' }} />
        <div className="relative text-center">
          <div className="w-16 h-16 bg-[#E8321A] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-red">
            <span className="font-display text-white font-bold text-3xl italic">y</span>
          </div>
          <h2 className="font-display text-4xl text-white font-semibold mb-4">
            Join thousands of<br /><em className="text-[#E8321A]">food lovers</em>
          </h2>
          <p className="text-[rgba(253,248,243,0.5)] text-lg max-w-sm">
            Discover restaurants, write reviews, and save your favorites.
          </p>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 overflow-y-auto">
        <div className="w-full max-w-md py-8 scale-in">
          <div className="lg:hidden flex items-center gap-2.5 mb-8">
            <div className="w-10 h-10 bg-[#E8321A] rounded-xl flex items-center justify-center">
              <span className="font-display text-white font-bold text-xl italic">y</span>
            </div>
            <span className="font-display text-2xl font-semibold">yelp<span className="text-[#E8321A]">.</span></span>
          </div>

          <h1 className="font-display text-3xl font-semibold text-[#1A1208] mb-1">Create account</h1>
          <p className="text-[#8C7E6E] mb-8">Start discovering great restaurants</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map(f => (
              <div key={f.name} className="float-wrap">
                <input type={f.type} value={form[f.name]}
                  onChange={e => setForm({...form, [f.name]: e.target.value})}
                  placeholder=" " required className="float-input" id={f.name} />
                <label htmlFor={f.name} className="float-label">{f.label}</label>
              </div>
            ))}

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl"
                style={{ background: 'rgba(232,50,26,0.08)', border: '1px solid rgba(232,50,26,0.2)' }}>
                <span style={{ fontSize: 14, color: 'var(--red)' }}>⚠</span>
                <p style={{ fontSize: 13, color: 'var(--red)' }}>{error}</p>
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3.5 rounded-xl text-base">
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="divider" />
          <p style={{ fontSize: 14, color: 'var(--muted)', textAlign: 'center' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--red)', fontWeight: 600 }} className="hover:underline">Sign in</Link>
          </p>
          <p style={{ fontSize: 13, color: 'var(--muted)', textAlign: 'center', marginTop: 12 }}>
            Restaurant owner?{' '}
            <Link to="/owner/signup" style={{ color: 'var(--ink)', fontWeight: 500 }} className="hover:text-[var(--red)] transition-colors">Register as owner →</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
