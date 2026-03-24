import { useState, useEffect } from 'react'
import { getHistory } from '../services/api'
import { Link } from 'react-router-dom'
import StarRating from '../components/StarRating'
import LoadingSpinner from '../components/LoadingSpinner'

export default function HistoryPage() {
  const [history, setHistory] = useState({ reviews: [], restaurants_added: [] })
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('reviews')

  useEffect(() => {
    getHistory()
      .then((res) => setHistory(res.data || { reviews: [], restaurants_added: [] }))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 slide-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" style={{ fontFamily: "'Playfair Display', serif" }}>
          My History
        </h1>
        <p className="text-sm text-gray-500 mt-1">Your activity on Yelp</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 w-fit">
        <button
          onClick={() => setTab('reviews')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${tab === 'reviews' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          ✍️ Reviews ({history.reviews?.length || 0})
        </button>
        <button
          onClick={() => setTab('added')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${tab === 'added' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          🍽️ Added ({history.restaurants_added?.length || 0})
        </button>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading history..." />
      ) : tab === 'reviews' ? (
        history.reviews?.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-5xl mb-3">✍️</div>
            <p className="text-gray-500 font-medium">No reviews yet</p>
            <p className="text-sm text-gray-400 mt-1">Your reviews will appear here</p>
            <Link to="/" className="inline-block mt-4 px-5 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700">
              Explore Restaurants
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {history.reviews.map((r) => (
              <Link key={r.review_id} to={`/restaurants/${r.restaurant_id}`} className="block">
                <div className="bg-white rounded-xl border border-gray-100 p-5 hover:border-red-200 hover:shadow-sm transition-all">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{r.restaurant_name || `Restaurant #${r.restaurant_id}`}</h3>
                    <span className="text-xs text-gray-400">{formatDate(r.date)}</span>
                  </div>
                  <StarRating value={r.rating} readOnly size="sm" />
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">{r.comment}</p>
                </div>
              </Link>
            ))}
          </div>
        )
      ) : (
        history.restaurants_added?.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-5xl mb-3">🍽️</div>
            <p className="text-gray-500 font-medium">You haven't added any restaurants</p>
            <Link to="/add-restaurant" className="inline-block mt-4 px-5 py-2.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700">
              Add a Restaurant
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {history.restaurants_added.map((r) => (
              <Link key={r.id} to={`/restaurants/${r.id}`} className="block">
                <div className="bg-white rounded-xl border border-gray-100 p-5 hover:border-red-200 hover:shadow-sm transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{r.name}</h3>
                    <span className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-full">{r.cuisine}</span>
                  </div>
                  {r.address && <p className="text-xs text-gray-400">📍 {r.address}</p>}
                </div>
              </Link>
            ))}
          </div>
        )
      )}
    </div>
  )
}
