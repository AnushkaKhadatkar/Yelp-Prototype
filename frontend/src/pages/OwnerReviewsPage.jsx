import { useState, useEffect } from 'react'
import { getOwnerRestaurantReviews, getOwnerProfile } from '../services/api'
import StarRating from '../components/StarRating'
import LoadingSpinner from '../components/LoadingSpinner'

export default function OwnerReviewsPage() {
  const [reviews, setReviews] = useState([])
  const [restaurants, setRestaurants] = useState([])
  const [loading, setLoading] = useState(true)
  const [restaurantId, setRestaurantId] = useState(null)
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('newest')

  useEffect(() => {
    getOwnerProfile()
      .then((res) => {
        console.log('Owner profile data:', res.data)
        const rests = res.data.restaurants || []
        setRestaurants(rests)
        const id = rests[0]?.id
        console.log('Restaurant ID found:', id)
        if (id) {
          setRestaurantId(id)
          return getOwnerRestaurantReviews(id)
        }
        return { data: [] }
      })
      .then((res) => setReviews(res.data.reviews || res.data || []))
      .catch((err) => console.error('Error:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleRestaurantChange = (id) => {
    setLoading(true)
    setRestaurantId(id)
    getOwnerRestaurantReviews(id)
      .then((res) => setReviews(res.data.reviews || res.data || []))
      .catch((err) => console.error('Error:', err))
      .finally(() => setLoading(false))
  }

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

  const filtered = reviews
    .filter((r) => filter === 'all' || r.rating === parseInt(filter))
    .sort((a, b) => {
      if (sortBy === 'newest') return new Date(b.date) - new Date(a.date)
      if (sortBy === 'oldest') return new Date(a.date) - new Date(b.date)
      if (sortBy === 'highest') return b.rating - a.rating
      if (sortBy === 'lowest') return a.rating - b.rating
      return 0
    })

  const avgRating = reviews.length ? (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1) : null

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 slide-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" style={{ fontFamily: "'Playfair Display', serif" }}>
          Customer Reviews
        </h1>
        <p className="text-sm text-gray-500 mt-1">Read-only view of all reviews for your restaurant</p>

        {/* ✅ RESTAURANT SELECTOR — only shows if owner has multiple */}
        {restaurants.length > 1 && (
          <select
            value={restaurantId || ''}
            onChange={(e) => handleRestaurantChange(parseInt(e.target.value))}
            className="mt-3 px-3 py-2 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-200"
          >
            {restaurants.map((r) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        )}
      </div>

      {loading ? (
        <LoadingSpinner text="Loading reviews..." />
      ) : reviews.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
          <span className="text-5xl">💬</span>
          <p className="text-gray-500 font-medium mt-3">No reviews yet</p>
          <p className="text-sm text-gray-400 mt-1">Reviews will appear here once customers start leaving feedback</p>
        </div>
      ) : (
        <>
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-2xl border border-gray-100 p-5 text-center shadow-sm">
              <p className="text-3xl font-bold text-gray-900">{reviews.length}</p>
              <p className="text-sm text-gray-500 mt-1">Total Reviews</p>
            </div>
            <div className="bg-white rounded-2xl border border-gray-100 p-5 text-center shadow-sm">
              <p className="text-3xl font-bold text-yellow-500">{avgRating}</p>
              <p className="text-sm text-gray-500 mt-1">Avg Rating</p>
            </div>
            <div className="bg-white rounded-2xl border border-gray-100 p-5 text-center shadow-sm">
              <p className="text-3xl font-bold text-green-600">{reviews.filter(r => r.rating >= 4).length}</p>
              <p className="text-sm text-gray-500 mt-1">Positive (4-5★)</p>
            </div>
          </div>

          {/* Filter / Sort Bar */}
          <div className="flex flex-col sm:flex-row gap-3 mb-5">
            <div className="flex gap-2 flex-wrap">
              {['all', '5', '4', '3', '2', '1'].map((f) => (
                <button key={f} onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 text-xs rounded-full border transition-all font-medium ${filter === f ? 'bg-red-600 text-white border-red-600' : 'border-gray-200 text-gray-600 hover:border-red-300'}`}
                >
                  {f === 'all' ? 'All' : `${f}★`}
                </button>
              ))}
            </div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sm:ml-auto px-3 py-1.5 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-200"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="highest">Highest Rating</option>
              <option value="lowest">Lowest Rating</option>
            </select>
          </div>

          {/* Reviews List */}
          <div className="space-y-4">
            {filtered.length === 0 ? (
              <p className="text-center text-gray-400 py-8">No reviews match this filter</p>
            ) : (
              filtered.map((r) => (
                <div key={r.review_id} className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm fade-in">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-red-600 font-semibold text-sm">{r.user_name?.[0]?.toUpperCase() || 'U'}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">{r.user_name || 'Anonymous'}</p>
                        <p className="text-xs text-gray-400">{formatDate(r.date)}</p>
                      </div>
                    </div>
                    <StarRating value={r.rating} readOnly size="sm" />
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">{r.comment}</p>
                  {r.photos && r.photos.length > 0 && (
                    <div className="flex gap-2 mt-3">
                      {r.photos.map((p, i) => (
                        <img key={i} src={`http://localhost:8000${p}`} alt="review" className="w-16 h-16 object-cover rounded-lg" />
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}