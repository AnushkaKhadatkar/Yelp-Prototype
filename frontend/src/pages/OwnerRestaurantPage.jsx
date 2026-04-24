import { useState, useEffect, useRef } from 'react'
import { getOwnerProfile, updateOwnerProfile } from '../services/api'
import API from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'

const CUISINE_OPTIONS = ['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'American', 'French', 'Mediterranean', 'Thai', 'Korean', 'Vietnamese', 'Greek', 'Spanish', 'Other']
const PRICE_TIERS = ['$', '$$', '$$$', '$$$$']

function normalizeOwnerProfilePayload(data) {
  const owner = data?.owner || {
    id: data?.id,
    name: data?.name,
    email: data?.email,
  }
  const restaurants = data?.restaurants || data?.restaurant_details || []
  return { owner, restaurants }
}

async function waitForEventSaved(eventId, timeoutMs = 8000) {
  if (!eventId) return
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await API.get(`/events/status/${eventId}`)
      const status = res?.data?.status
      if (status === 'saved' || status === 'failed') return
    } catch {
      // ignore transient 404 while worker has not written status yet
    }
    await new Promise((r) => setTimeout(r, 400))
  }
}

export default function OwnerRestaurantPage() {
  const { user, role, login } = useAuth()
  const [tab, setTab] = useState('profile')
  const [profile, setProfile] = useState({ name: '', email: '', restaurant_name: '', cuisine: '', description: '', location: '', contact: '', hours: '' })
  const [newRest, setNewRest] = useState({ name: '', cuisine: '', description: '', address: '', city: '', contact_phone: '', contact_email: '', hours: '', pricing_tier: '', amenities: '' })
  const [photos, setPhotos] = useState([]) // for new restaurant
  const [photosPreviews, setPhotosPreviews] = useState([])
  const photosRef = useRef()

  // For editing existing restaurant photos
  const [myRestaurantId, setMyRestaurantId] = useState(null)
  const [myRestaurants, setMyRestaurants] = useState([])
  const [uploadingPhotos, setUploadingPhotos] = useState(false)
  const existingPhotosRef = useRef()

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    getOwnerProfile()
      .then((res) => {
        const { owner, restaurants } = normalizeOwnerProfilePayload(res.data)
        const rest = restaurants[0] || {}
        setMyRestaurantId(rest.id || null)
        setMyRestaurants(restaurants)
        setProfile({
          name: owner.name || '',
          email: owner.email || '',
          restaurant_name: rest.name || '',
          cuisine: rest.cuisine || '',
          description: rest.description || '',
          location: rest.city || '',
          contact: rest.contact_phone || '',
          hours: rest.hours || '',
        })
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handlePhotoSelect = (e) => {
    const files = Array.from(e.target.files)
    setPhotos(files)
    setPhotosPreviews(files.map(f => URL.createObjectURL(f)))
  }

  const handleProfileSave = async (e) => {
    e.preventDefault()
    setSaving(true); setSuccess(''); setError('')
    try {
      await updateOwnerProfile({ name: profile.name, email: profile.email })
      login(
        { ...(user || {}), name: profile.name, email: profile.email },
        role || 'owner',
        localStorage.getItem('token')
      )
      setSuccess('Profile updated!')
    } catch (e) {
      const detail = e.response?.data?.detail
      if (Array.isArray(detail)) setError(detail.map(d => d.msg).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Failed to update profile.')
    }
    setSaving(false)
    setTimeout(() => setSuccess(''), 3000)
  }

  const handleAddRestaurant = async (e) => {
    e.preventDefault()
    setSaving(true); setSuccess(''); setError('')
    try {
      // Backend uses Form fields — send as FormData
      const formData = new FormData()
      formData.append('name', newRest.name)
      formData.append('cuisine', newRest.cuisine)
      if (newRest.description) formData.append('description', newRest.description)
      if (newRest.address) formData.append('address', newRest.address)
      if (newRest.city) formData.append('city', newRest.city)
      if (newRest.contact_phone) formData.append('contact_phone', newRest.contact_phone)
      if (newRest.contact_email) formData.append('contact_email', newRest.contact_email)
      if (newRest.hours) formData.append('hours', newRest.hours)
      if (newRest.pricing_tier) formData.append('pricing_tier', newRest.pricing_tier)
      if (newRest.amenities) formData.append('amenities', newRest.amenities)
      // Attach photos
      photos.forEach(photo => formData.append('photos', photo))

      const createRes = await API.post('/owner/restaurants', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await waitForEventSaved(createRes?.data?.eventId)
      // Refresh owner restaurants after async create is accepted.
      const refreshed = await getOwnerProfile()
      const { restaurants } = normalizeOwnerProfilePayload(refreshed.data)
      setMyRestaurants(restaurants)
      setMyRestaurantId(restaurants[0]?.id || null)
      setSuccess('Restaurant posted successfully!')
      setNewRest({ name: '', cuisine: '', description: '', address: '', city: '', contact_phone: '', contact_email: '', hours: '', pricing_tier: '', amenities: '' })
      setPhotos([])
      setPhotosPreviews([])
    } catch (e) {
      const detail = e.response?.data?.detail
      if (Array.isArray(detail)) setError(detail.map(d => d.msg).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Failed to post restaurant.')
    }
    setSaving(false)
    setTimeout(() => setSuccess(''), 3000)
  }

  const handleUploadPhotosToExisting = async (e) => {
    const files = Array.from(e.target.files)
    if (!files.length || !myRestaurantId) return
    setUploadingPhotos(true)
    try {
      const formData = new FormData()
      files.forEach(f => formData.append('photos', f))
      await API.post(`/restaurants/${myRestaurantId}/photos`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccess('Photos uploaded!')
    } catch (e) {
      setError('Failed to upload photos.')
    }
    setUploadingPhotos(false)
    setTimeout(() => setSuccess(''), 3000)
  }

  if (loading) return <div className="max-w-3xl mx-auto px-4 py-8"><LoadingSpinner /></div>

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 slide-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6" style={{ fontFamily: "'Playfair Display', serif" }}>My Restaurant</h1>

      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-8 w-fit">
        {['profile', 'post', 'photos'].map((t) => (
          <button key={t} onClick={() => { setTab(t); setSuccess(''); setError('') }}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${tab === t ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {t === 'profile' ? '🏪 Profile' : t === 'post' ? '➕ Post New' : '📷 Photos'}
          </button>
        ))}
      </div>

      {success && <div className="mb-4 px-4 py-3 bg-green-50 text-green-700 rounded-xl text-sm border border-green-200">{success}</div>}
      {error && <div className="mb-4 px-4 py-3 bg-red-50 text-red-600 rounded-xl text-sm border border-red-200">{error}</div>}

      {/* Profile Tab */}
      {tab === 'profile' && (
        <form onSubmit={handleProfileSave} className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8 space-y-5 shadow-sm">
          <h2 className="font-semibold text-gray-900">Owner Profile</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Your Name</label>
              <input type="text" value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
          </div>

          {/* My Restaurants List */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              🍽️ My Restaurants ({myRestaurants.length})
            </h3>
            {myRestaurants.length === 0 ? (
              <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-500 text-center">
                You haven't posted any restaurants yet.
                <button type="button" onClick={() => setTab('post')}
                  className="ml-2 text-red-600 font-medium hover:underline">
                  Post one now →
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {myRestaurants.map((r) => (
                  <div key={r.id} className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3">
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{r.name}</p>
                      <p className="text-xs text-gray-400">{r.cuisine} · {r.city} · ⭐ {r.avg_rating || 0}</p>
                    </div>
                    <a href={`/restaurants/${r.id}`}
                      className="text-xs text-red-600 font-medium hover:underline px-3 py-1.5 bg-red-50 rounded-lg">
                      View →
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button type="submit" disabled={saving}
            className="px-8 py-3 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 disabled:opacity-50 transition-colors text-sm">
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      )}

      {/* Post New Restaurant Tab */}
      {tab === 'post' && (
        <form onSubmit={handleAddRestaurant} className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8 space-y-5 shadow-sm">
          <h2 className="font-semibold text-gray-900">Post a New Restaurant Listing</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Restaurant Name <span className="text-red-500">*</span></label>
              <input type="text" required value={newRest.name} onChange={(e) => setNewRest({ ...newRest, name: e.target.value })}
                placeholder="e.g. Bella Italia"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Cuisine <span className="text-red-500">*</span></label>
              <select required value={newRest.cuisine} onChange={(e) => setNewRest({ ...newRest, cuisine: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-200">
                <option value="">Select cuisine</option>
                {CUISINE_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">City</label>
              <input type="text" value={newRest.city} onChange={(e) => setNewRest({ ...newRest, city: e.target.value })}
                placeholder="San Jose"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
              <input type="text" value={newRest.address} onChange={(e) => setNewRest({ ...newRest, address: e.target.value })}
                placeholder="123 Main St"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Phone</label>
              <input type="text" value={newRest.contact_phone} onChange={(e) => setNewRest({ ...newRest, contact_phone: e.target.value })}
                placeholder="(408) 555-0123"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Hours</label>
              <input type="text" value={newRest.hours} onChange={(e) => setNewRest({ ...newRest, hours: e.target.value })}
                placeholder="Mon–Fri 11am–10pm"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Amenities</label>
              <input type="text" value={newRest.amenities} onChange={(e) => setNewRest({ ...newRest, amenities: e.target.value })}
                placeholder="WiFi, Parking, Outdoor..."
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Pricing Tier</label>
              <div className="flex gap-2">
                {PRICE_TIERS.map((p) => (
                  <button key={p} type="button" onClick={() => setNewRest({ ...newRest, pricing_tier: p })}
                    className={`flex-1 py-2.5 text-sm rounded-xl border font-medium transition-all ${newRest.pricing_tier === p ? 'bg-red-600 text-white border-red-600' : 'border-gray-200 text-gray-600 hover:border-red-300'}`}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
              <textarea value={newRest.description} onChange={(e) => setNewRest({ ...newRest, description: e.target.value })}
                rows={3} placeholder="Describe your restaurant..."
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 resize-none" />
            </div>

            {/* Photo Upload */}
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1.5">📷 Restaurant Photos (optional)</label>
              <input ref={photosRef} type="file" accept="image/*" multiple className="hidden" onChange={handlePhotoSelect} />
              <button type="button" onClick={() => photosRef.current.click()}
                className="px-4 py-2.5 border-2 border-dashed border-gray-300 hover:border-red-300 rounded-xl text-sm text-gray-500 hover:text-red-600 transition-all w-full">
                {photos.length > 0 ? `${photos.length} photo(s) selected` : '+ Click to add photos'}
              </button>
              {photosPreviews.length > 0 && (
                <div className="flex gap-2 mt-3 flex-wrap">
                  {photosPreviews.map((url, i) => (
                    <img key={i} src={url} alt="preview" className="w-20 h-20 object-cover rounded-lg border" />
                  ))}
                </div>
              )}
            </div>
          </div>

          <button type="submit" disabled={saving}
            className="px-8 py-3 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 disabled:opacity-50 transition-colors text-sm">
            {saving ? 'Posting...' : '🚀 Post Restaurant'}
          </button>
        </form>
      )}

      {/* Photos Tab */}
      {tab === 'photos' && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-2">Upload Photos to Your Restaurant</h2>
          {!myRestaurantId ? (
            <div className="text-center py-10">
              <p className="text-gray-500 text-sm">You don't have a restaurant listed yet.</p>
              <button onClick={() => setTab('post')} className="mt-3 px-4 py-2 bg-red-600 text-white rounded-xl text-sm hover:bg-red-700">
                Post a Restaurant First
              </button>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-500 mb-4">Add photos to your existing restaurant listing.</p>
              <input ref={existingPhotosRef} type="file" accept="image/*" multiple className="hidden" onChange={handleUploadPhotosToExisting} />
              <button type="button" onClick={() => existingPhotosRef.current.click()} disabled={uploadingPhotos}
                className="px-6 py-3 border-2 border-dashed border-gray-300 hover:border-red-300 rounded-xl text-sm text-gray-500 hover:text-red-600 transition-all w-full">
                {uploadingPhotos ? 'Uploading...' : '📷 Select & Upload Photos'}
              </button>
              <p className="text-xs text-gray-400 mt-2">You can select multiple photos at once. They will be added to your restaurant listing immediately.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
