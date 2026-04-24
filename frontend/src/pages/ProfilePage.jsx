import { useState, useEffect, useRef } from 'react'
import { getUserProfile, updateUserProfile, uploadProfilePicture, getUserPreferences, updateUserPreferences } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { toMediaUrl } from '../utils/mediaUrl'

const COUNTRIES = ['United States', 'Canada', 'United Kingdom', 'India', 'Australia', 'Germany', 'France', 'Japan', 'China', 'Brazil', 'Mexico', 'Italy', 'Spain', 'Other']
const CUISINES_LIST = ['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'American', 'French', 'Mediterranean', 'Thai', 'Korean', 'Vietnamese', 'Greek', 'Spanish']
const DIETARY = ['Vegetarian', 'Vegan', 'Halal', 'Kosher', 'Gluten-Free', 'Dairy-Free', 'Nut-Free']
const AMBIANCE = ['Casual', 'Fine Dining', 'Family-Friendly', 'Romantic', 'Business', 'Outdoor', 'Trendy', 'Cozy']
const SORT_OPTIONS = ['Rating', 'Distance', 'Popularity', 'Price']
const PRICE_RANGES = ['$', '$$', '$$$', '$$$$']

function MultiSelect({ options, selected = [], onChange, label }) {
  const arr = Array.isArray(selected) ? selected : (selected ? [selected] : [])
  const toggle = (opt) => {
    if (arr.includes(opt)) onChange(arr.filter((o) => o !== opt))
    else onChange([...arr, opt])
  }
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => (
          <button key={opt} type="button" onClick={() => toggle(opt)}
            className={`px-3 py-1.5 text-xs rounded-full border transition-all ${arr.includes(opt) ? 'bg-red-600 text-white border-red-600' : 'border-gray-200 text-gray-600 hover:border-red-300 hover:text-red-600'}`}>
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ProfilePage() {
  const { user, login, role } = useAuth()
  const [tab, setTab] = useState('profile')
  const [profile, setProfile] = useState({ name: '', email: '', phone: '', about: '', city: '', country: '', languages: '', gender: '' })
  const [prefs, setPrefs] = useState({ cuisines: [], price_range: '', location: '', dietary_needs: [], ambiance: [], sort_preference: '' })
  const [profileLoading, setProfileLoading] = useState(true)
  const [prefsLoading, setPrefsLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [picUrl, setPicUrl] = useState('')
  const [picLoading, setPicLoading] = useState(false)
  const fileRef = useRef()

  useEffect(() => {
    getUserProfile().then((res) => {
      const d = res.data
      setProfile({
        name: d.name || '',
        email: d.email || '',
        phone: d.phone || '',
        about: d.about || '',
        city: d.city || '',
        country: d.country || '',
        languages: d.languages || '',
        gender: d.gender || '',
      })
      if (d.profile_pic) {
        setPicUrl(toMediaUrl(d.profile_pic))
      }
      setProfileLoading(false)
    }).catch(() => setProfileLoading(false))

    getUserPreferences().then((res) => {
      const d = res.data
      const parse = (val) => {
        if (Array.isArray(val)) return val
        if (!val) return []
        try { return JSON.parse(val) } catch { return val.split(',').filter(Boolean) }
      }
      setPrefs({
        cuisines: parse(d.cuisines),
        price_range: d.price_range || '',
        location: d.location || '',
        dietary_needs: parse(d.dietary_needs),
        ambiance: parse(d.ambiance),
        sort_preference: d.sort_preference || '',
      })
      setPrefsLoading(false)
    }).catch(() => setPrefsLoading(false))
  }, [])

  const handleProfileSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSuccess('')
    setError('')
    try {
      await updateUserProfile(profile)
      setSuccess('Profile updated successfully!')
      login({ ...user, name: profile.name }, role, localStorage.getItem('token'))
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail[0]?.msg || 'Validation error')
      } else {
        setError(typeof detail === 'string' ? detail : 'Failed to update profile.')
      }
    } finally {
      setSaving(false)
      setTimeout(() => setSuccess(''), 3000)
    }
  }

  const handlePrefsSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSuccess('')
    setError('')
    try {
      await updateUserPreferences({
        cuisines: prefs.cuisines,
        price_range: prefs.price_range,
        location: prefs.location,
        dietary_needs: prefs.dietary_needs,
        ambiance: prefs.ambiance,
        sort_preference: prefs.sort_preference,
      })
      setSuccess('Preferences saved!')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail[0]?.msg || 'Validation error')
      } else {
        setError(typeof detail === 'string' ? detail : 'Failed to save preferences.')
      }
    } finally {
      setSaving(false)
      setTimeout(() => setSuccess(''), 3000)
    }
  }

  const handlePicUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    e.target.value = ''
    const formData = new FormData()
    formData.append('file', file)
    setPicLoading(true)
    try {
      await uploadProfilePicture(formData)
      const localUrl = URL.createObjectURL(file)
      setPicUrl(localUrl)
    } catch (err) {
      setError('Failed to upload photo.')
    }
    setPicLoading(false)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 slide-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6" style={{ fontFamily: "'Playfair Display', serif" }}>My Account</h1>

      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-8 w-fit">
        {['profile', 'preferences'].map((t) => (
          <button key={t} onClick={() => { setTab(t); setSuccess(''); setError('') }}
            className={`px-5 py-2 rounded-lg text-sm font-medium capitalize transition-all ${tab === t ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {t === 'profile' ? '👤 Profile' : '⚙️ Preferences'}
          </button>
        ))}
      </div>

      {success && <div className="mb-4 px-4 py-3 bg-green-50 text-green-700 rounded-xl text-sm border border-green-200">{success}</div>}
      {error && <div className="mb-4 px-4 py-3 bg-red-50 text-red-600 rounded-xl text-sm border border-red-200">{error}</div>}

      {tab === 'profile' && !profileLoading && (
        <form onSubmit={handleProfileSave} className="space-y-6">
          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-semibold text-gray-900 mb-4">Profile Photo</h2>
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-full overflow-hidden bg-red-100 flex-shrink-0 border-2 border-red-200">
                {picUrl ? (
                  <img src={picUrl} alt="profile" className="w-full h-full object-cover" key={picUrl} />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <span className="text-red-600 font-bold text-2xl">{profile.name?.[0]?.toUpperCase() || 'U'}</span>
                  </div>
                )}
              </div>
              <div>
                <button type="button" onClick={() => fileRef.current.click()} disabled={picLoading}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-sm text-gray-700 rounded-lg font-medium transition-colors">
                  {picLoading ? 'Uploading...' : picUrl ? 'Change Photo' : 'Upload Photo'}
                </button>
                <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handlePicUpload} />
                <p className="text-xs text-gray-400 mt-1">JPG, PNG up to 5MB</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-semibold text-gray-900 mb-4">Personal Information</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { name: 'name', label: 'Full Name', type: 'text' },
                { name: 'email', label: 'Email', type: 'email' },
                { name: 'phone', label: 'Phone Number', type: 'tel' },
                { name: 'city', label: 'City', type: 'text' },
              ].map((f) => (
                <div key={f.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">{f.label}</label>
                  <input name={f.name} type={f.type} value={profile[f.name]}
                    onChange={(e) => setProfile({ ...profile, [e.target.name]: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Country</label>
                <select value={profile.country} onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 bg-white">
                  <option value="">Select country</option>
                  {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Gender</label>
                <select value={profile.gender} onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 bg-white">
                  <option value="">Prefer not to say</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Non-binary">Non-binary</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Languages</label>
                <input type="text" value={profile.languages}
                  onChange={(e) => setProfile({ ...profile, languages: e.target.value })}
                  placeholder="English, Spanish..."
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">About Me</label>
              <textarea value={profile.about} onChange={(e) => setProfile({ ...profile, about: e.target.value })}
                rows={3} placeholder="Tell the community about yourself..."
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 resize-none" />
            </div>
          </div>

          <button type="submit" disabled={saving}
            className="px-8 py-3 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 disabled:opacity-50 transition-colors">
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      )}

      {tab === 'preferences' && !prefsLoading && (
        <form onSubmit={handlePrefsSave} className="space-y-6">
          <div className="bg-white rounded-2xl border border-gray-100 p-6 space-y-6">
            <div>
              <h2 className="font-semibold text-gray-900">AI Assistant Preferences</h2>
              <p className="text-sm text-gray-500 mt-1">These help the AI make better restaurant recommendations for you.</p>
            </div>
            <MultiSelect options={CUISINES_LIST} selected={prefs.cuisines}
              onChange={(v) => setPrefs({ ...prefs, cuisines: v })} label="Cuisine Preferences" />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
              <div className="flex gap-2">
                {PRICE_RANGES.map((p) => (
                  <button key={p} type="button" onClick={() => setPrefs({ ...prefs, price_range: p })}
                    className={`px-4 py-2 text-sm rounded-xl border transition-all font-medium ${prefs.price_range === p ? 'bg-red-600 text-white border-red-600' : 'border-gray-200 text-gray-600 hover:border-red-300'}`}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Preferred Location</label>
              <input type="text" value={prefs.location}
                onChange={(e) => setPrefs({ ...prefs, location: e.target.value })}
                placeholder="e.g. San Jose, CA"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <MultiSelect options={DIETARY} selected={prefs.dietary_needs}
              onChange={(v) => setPrefs({ ...prefs, dietary_needs: v })} label="Dietary Needs" />
            <MultiSelect options={AMBIANCE} selected={prefs.ambiance}
              onChange={(v) => setPrefs({ ...prefs, ambiance: v })} label="Ambiance Preferences" />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort Preference</label>
              <div className="flex flex-wrap gap-2">
                {SORT_OPTIONS.map((s) => (
                  <button key={s} type="button" onClick={() => setPrefs({ ...prefs, sort_preference: s })}
                    className={`px-4 py-2 text-sm rounded-full border transition-all ${prefs.sort_preference === s ? 'bg-red-600 text-white border-red-600' : 'border-gray-200 text-gray-600 hover:border-red-300'}`}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <button type="submit" disabled={saving}
            className="px-8 py-3 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 disabled:opacity-50 transition-colors">
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </form>
      )}
    </div>
  )
}