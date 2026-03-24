import { useState, useEffect } from 'react'
import { getOwnerDashboard } from '../services/api'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

function StatCard({ label, value, icon, color = 'red' }) {
  const colors = { red: 'bg-red-50 text-red-600', blue: 'bg-blue-50 text-blue-600', green: 'bg-green-50 text-green-600', orange: 'bg-orange-50 text-orange-600' }
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
      <div className={`inline-flex w-10 h-10 rounded-xl items-center justify-center text-lg mb-3 ${colors[color]}`}>{icon}</div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500 mt-0.5">{label}</p>
    </div>
  )
}

function RatingBar({ star, count, total }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-500 w-4">{star}</span>
      <span className="text-yellow-500 text-sm">★</span>
      <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
        <div className="bg-yellow-400 h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm text-gray-400 w-6 text-right">{count}</span>
    </div>
  )
}

export default function OwnerDashboardPage() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOwnerDashboard()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-8"><LoadingSpinner text="Loading dashboard..." /></div>

  // Backend returns: total_review_count, avg_rating, ratings_distribution, recent_reviews, sentiment_summary
  const totalRatings = data?.total_review_count || 0
  const distribution = data?.ratings_distribution || {}

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 slide-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" style={{ fontFamily: "'Playfair Display', serif" }}>Owner Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Welcome back, {user?.name} 👋</p>
      </div>

      {!data ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
          <span className="text-5xl">📊</span>
          <p className="text-gray-500 mt-3 font-medium">No data yet</p>
        </div>
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            <StatCard label="Total Reviews" value={totalRatings} icon="💬" color="green" />
            <StatCard label="Average Rating" value={data.avg_rating ? `${data.avg_rating} ★` : '—'} icon="⭐" color="orange" />
            <StatCard label="Positive Reviews" value={Object.entries(distribution).filter(([k]) => parseInt(k) >= 4).reduce((s, [,v]) => s + v, 0)} icon="👍" color="blue" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Rating Distribution */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
              <h2 className="font-semibold text-gray-900 mb-4">Rating Distribution</h2>
              <div className="space-y-3">
                {[5, 4, 3, 2, 1].map((star) => (
                  <RatingBar key={star} star={star} count={distribution[star] || 0} total={totalRatings} />
                ))}
              </div>
            </div>

            {/* Sentiment */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
              <h2 className="font-semibold text-gray-900 mb-4">Sentiment Summary</h2>
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-sm text-gray-700 leading-relaxed">{data.sentiment_summary || 'No reviews yet.'}</p>
              </div>
            </div>
          </div>

          {/* Recent Reviews */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
            <h2 className="font-semibold text-gray-900 mb-4">Recent Reviews</h2>
            {!data.recent_reviews || data.recent_reviews.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">No reviews yet</p>
            ) : (
              <div className="space-y-4">
                {data.recent_reviews.map((r, i) => (
                  <div key={i} className="flex items-start gap-4 pb-4 border-b border-gray-50 last:border-0 last:pb-0">
                    <div className="w-9 h-9 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-red-600 font-semibold text-sm">★</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-800">{r.restaurant_name}</span>
                        <span className="text-xs text-gray-400">{formatDate(r.created_at)}</span>
                        <span className="text-yellow-500 text-xs">{r.rating}★</span>
                      </div>
                      <p className="text-sm text-gray-600">{r.comment}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
