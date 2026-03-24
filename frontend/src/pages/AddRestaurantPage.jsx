import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRestaurant } from '../services/api'

const CUISINE_OPTIONS = ['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'American', 'French', 'Mediterranean', 'Thai', 'Korean', 'Vietnamese', 'Greek', 'Spanish', 'Other']
const PRICE_TIERS = ['$', '$$', '$$$', '$$$$']
const US_STATES = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

export default function AddRestaurantPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', cuisine: '', address: '', city: '', state: '', zip_code: '',
    contact_phone: '', contact_email: '', description: '', hours: '',
    pricing_tier: '', ambiance: '', amenities: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [photos, setPhotos] = useState([])
  const [photoPreviews, setPhotoPreviews] = useState([])
  const photosRef = useRef()

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.name || !form.cuisine || !form.address || !form.city || !form.state || !form.zip_code) {
      setError('Please fill in all required fields (name, cuisine, address, city, state, zip code).')
      return
    }
    setLoading(true)
    try {
      const formData = new FormData()
      Object.entries(form).forEach(([key, val]) => {
        if (val) formData.append(key, val)
      })
      // Attach photos if any
      photos.forEach(photo => formData.append('photos', photo))
      const res = await createRestaurant(formData)
      navigate(`/restaurants/${res.data.restaurant_id}`)
    } catch (e) {
      const detail = e.response?.data?.detail
      if (Array.isArray(detail)) setError(detail.map(d => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join(', '))
      else setError(typeof detail === 'string' ? detail : 'Failed to create restaurant. Please try again.')
    }
    setLoading(false)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 slide-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" style={{ fontFamily: "'Playfair Display', serif" }}>
          Add a Restaurant
        </h1>
        <p className="text-gray-500 text-sm mt-1">Help others discover great places to eat</p>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 p-6 sm:p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Required Fields */}
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">Required Information</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Restaurant Name <span className="text-red-500">*</span>
                </label>
                <input name="name" type="text" value={form.name} onChange={handleChange} required
                  placeholder="e.g. Pasta Paradise"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Cuisine Type <span className="text-red-500">*</span>
                </label>
                <select name="cuisine" value={form.cuisine} onChange={handleChange} required
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 bg-white">
                  <option value="">Select cuisine</option>
                  {CUISINE_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  City <span className="text-red-500">*</span>
                </label>
                <input name="city" type="text" value={form.city} onChange={handleChange} required
                  placeholder="San Jose"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Street Address <span className="text-red-500">*</span>
                </label>
                <input name="address" type="text" value={form.address} onChange={handleChange} required
                  placeholder="123 Main Street"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  State <span className="text-red-500">*</span>
                </label>
                <select name="state" value={form.state} onChange={handleChange} required
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 bg-white">
                  <option value="">Select state</option>
                  {US_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Zip Code <span className="text-red-500">*</span>
                </label>
                <input name="zip_code" type="text" value={form.zip_code} onChange={handleChange} required
                  placeholder="95101"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>
            </div>
          </div>

          {/* Optional Fields */}
          <div className="border-t border-gray-100 pt-5">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">Optional Details</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Phone</label>
                <input name="contact_phone" type="text" value={form.contact_phone} onChange={handleChange}
                  placeholder="(408) 555-0123"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
                <input name="contact_email" type="email" value={form.contact_email} onChange={handleChange}
                  placeholder="info@restaurant.com"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Hours</label>
                <input name="hours" type="text" value={form.hours} onChange={handleChange}
                  placeholder="Mon–Fri 11am–10pm"
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Ambiance</label>
                <input name="ambiance" type="text" value={form.ambiance} onChange={handleChange}
                  placeholder="Casual, Romantic, Family-friendly..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Amenities</label>
                <input name="amenities" type="text" value={form.amenities} onChange={handleChange}
                  placeholder="WiFi, Parking, Outdoor seating..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Pricing Tier</label>
                <div className="flex gap-2">
                  {PRICE_TIERS.map(p => (
                    <button key={p} type="button"
                      onClick={() => setForm({ ...form, pricing_tier: p })}
                      className={`flex-1 py-3 text-sm rounded-xl border font-medium transition-all ${form.pricing_tier === p ? 'bg-red-600 text-white border-red-600' : 'border-gray-200 text-gray-600 hover:border-red-300'}`}>
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                <textarea name="description" value={form.description} onChange={handleChange} rows={4}
                  placeholder="Tell people what makes this restaurant special..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 resize-none" />
              </div>
            </div>
          </div>


          {/* Photo Upload */}
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1.5">📷 Restaurant Photos (optional)</label>
            <input ref={photosRef} type="file" accept="image/*" multiple className="hidden"
              onChange={(e) => {
                const files = Array.from(e.target.files)
                setPhotos(files)
                setPhotoPreviews(files.map(f => URL.createObjectURL(f)))
              }} />
            <button type="button" onClick={() => photosRef.current.click()}
              className="px-4 py-2.5 border-2 border-dashed border-gray-300 hover:border-red-300 rounded-xl text-sm text-gray-500 hover:text-red-600 transition-all w-full">
              {photos.length > 0 ? `${photos.length} photo(s) selected` : '+ Click to add photos'}
            </button>
            {photoPreviews.length > 0 && (
              <div className="flex gap-2 mt-3 flex-wrap">
                {photoPreviews.map((url, i) => (
                  <img key={i} src={url} alt="preview" className="w-20 h-20 object-cover rounded-lg border" />
                ))}
              </div>
            )}
          </div>
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-xl border border-red-100">{error}</div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={loading}
              className="flex-1 sm:flex-none px-8 py-3 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 disabled:opacity-50 transition-colors text-sm">
              {loading ? 'Adding...' : '+ Add Restaurant'}
            </button>
            <button type="button" onClick={() => navigate('/')}
              className="px-6 py-3 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-xl transition-colors">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
