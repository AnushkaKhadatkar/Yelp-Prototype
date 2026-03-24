import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getRestaurantById, createReview, addFavourite, removeFavourite, claimRestaurant, updateReview, deleteReview } from '../services/api'
import { useAuth } from '../context/AuthContext'
import StarRating from '../components/StarRating'
import LoadingSpinner from '../components/LoadingSpinner'

export default function RestaurantDetailsPage() {
  const { id } = useParams()
  const { user, isUser, isOwner } = useAuth()
  const navigate = useNavigate()

  const [restaurant, setRestaurant] = useState(null)
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isFav, setIsFav] = useState(false)
  const [favLoading, setFavLoading] = useState(false)

  // New review form
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [newRating, setNewRating] = useState(0)
  const [newComment, setNewComment] = useState('')
  const [reviewLoading, setReviewLoading] = useState(false)
  const [reviewError, setReviewError] = useState('')

  // Edit review
  const [editingReviewId, setEditingReviewId] = useState(null)
  const [editRating, setEditRating] = useState(0)
  const [editComment, setEditComment] = useState('')

  // Claim
  const [claimLoading, setClaimLoading] = useState(false)
  const [claimed, setClaimed] = useState(false)

  const loadRestaurant = async () => {
    setLoading(true)
    try {
      const res = await getRestaurantById(id)
      const data = res.data
      setRestaurant(data)
      // Reviews are included in the restaurant detail response
      setReviews(data.reviews || [])
    } catch {
      setError('Restaurant not found.')
    }
    setLoading(false)
  }

  useEffect(() => {
    loadRestaurant()
  }, [id])

  const handleFav = async () => {
    if (!user) { navigate('/login'); return }
    setFavLoading(true)
    try {
      if (isFav) { await removeFavourite(id); setIsFav(false) }
      else { await addFavourite(id); setIsFav(true) }
    } catch {}
    setFavLoading(false)
  }

  const handleSubmitReview = async (e) => {
    e.preventDefault()
    if (newRating === 0) { setReviewError('Please select a rating.'); return }
    setReviewLoading(true)
    setReviewError('')
    try {
      await createReview(id, { rating: newRating, comment: newComment })
      // Reload restaurant to get updated reviews + avg_rating
      await loadRestaurant()
      setNewRating(0)
      setNewComment('')
      setShowReviewForm(false)
    } catch (e) {
      const detail = e.response?.data?.detail
      setReviewError(typeof detail === 'string' ? detail : 'Failed to submit review.')
    }
    setReviewLoading(false)
  }

  const handleEditSave = async (reviewId) => {
    try {
      await updateReview(reviewId, { rating: editRating, comment: editComment })
      await loadRestaurant()
      setEditingReviewId(null)
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to update review.')
    }
  }

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Delete this review?')) return
    try {
      await deleteReview(reviewId)
      await loadRestaurant()
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to delete review.')
    }
  }

  const handleClaim = async () => {
    if (!window.confirm('Claim this restaurant?')) return
    setClaimLoading(true)
    try {
      await claimRestaurant(id)
      setClaimed(true)
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to claim restaurant.')
    }
    setClaimLoading(false)
  }

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-8"><LoadingSpinner text="Loading restaurant..." /></div>
  if (error) return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <p className="text-gray-500">{error}</p>
      <button onClick={() => navigate('/')} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm">Back to Home</button>
    </div>
  )

  const currentUserId = user?.id ? String(user.id) : null

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 slide-in">
      {/* Photo Banner */}
      {(() => {
        const CUISINE_PHOTOS = {
          Italian: 'https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=1200&q=80',
          Chinese: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=1200&q=80',
          Mexican: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=1200&q=80',
          Indian: 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=1200&q=80',
          Japanese: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=1200&q=80',
          American: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1200&q=80',
          French: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80',
          Mediterranean: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=1200&q=80',
          Thai: 'https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=1200&q=80',
          Korean: 'https://images.unsplash.com/photo-1583032015879-e5022cb87c3b?w=1200&q=80',
          Vietnamese: 'https://images.unsplash.com/photo-1628689469838-524a4a973b8e?w=1200&q=80',
          Greek: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=1200&q=80',
          Spanish: 'https://images.unsplash.com/photo-1515443961218-a51367888e4b?w=1200&q=80',
          Ethiopian: 'https://images.unsplash.com/photo-1567529692333-de9fd6772897?w=1200&q=80',
          Afghan: 'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=1200&q=80',
          Portuguese: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80',
          Burmese: 'https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=1200&q=80',
          Australian: 'https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=1200&q=80',
          Turkish: 'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=1200&q=80',
          Hawaiian: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1200&q=80',
        }
        const uploadedPhoto = restaurant.photos && restaurant.photos.length > 0
          ? `http://localhost:8000/uploads/${restaurant.photos[0]}`
          : null
        const bannerPhoto = uploadedPhoto || CUISINE_PHOTOS[restaurant.cuisine] || DEFAULT_PHOTO
        return (
      <div className="h-56 sm:h-72 bg-gradient-to-br from-red-100 to-orange-50 rounded-2xl mb-6 overflow-hidden relative">
        {bannerPhoto ? (
          <img src={bannerPhoto} alt={restaurant.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-8xl opacity-10">🍽️</span>
          </div>
        )}
        {isOwner && !restaurant.owner_id && !claimed && (
          <button onClick={handleClaim} disabled={claimLoading}
            className="absolute top-4 right-4 px-4 py-2 bg-white text-gray-800 text-sm font-medium rounded-xl shadow-md hover:bg-gray-50 transition-colors">
            {claimLoading ? 'Claiming...' : '🏷️ Claim Restaurant'}
          </button>
        )}
        {claimed && (
          <div className="absolute top-4 right-4 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-xl">✓ Claimed!</div>
        )}
      </div>
        )
      })()}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900" style={{ fontFamily: "'Playfair Display', serif" }}>
            {restaurant.name}
          </h1>
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            {restaurant.cuisine && <span className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full">{restaurant.cuisine}</span>}
            <div className="flex items-center gap-1">
              {[1,2,3,4,5].map(s => (
                <span key={s} style={{ color: s <= (restaurant.avg_rating || 0) ? '#f5a623' : '#d1d5db' }}>★</span>
              ))}
              <span className="text-sm text-gray-400 ml-1">({restaurant.avg_rating || 0}) · {restaurant.review_count || 0} reviews</span>
            </div>
          </div>
        </div>
        {isUser && (
          <div className="flex gap-2">
            <button onClick={handleFav} disabled={favLoading}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all ${isFav ? 'bg-red-600 text-white' : 'bg-red-50 text-red-600 hover:bg-red-100'}`}>
              {isFav ? '♥ Saved' : '♡ Save'}
            </button>
            <button onClick={() => setShowReviewForm(!showReviewForm)}
              className="flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-xl font-medium text-sm hover:bg-gray-800 transition-colors">
              ✍️ Write Review
            </button>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        {restaurant.address && (
          <div className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Address</p>
            <p className="text-sm text-gray-700">📍 {restaurant.address}{restaurant.city ? `, ${restaurant.city}` : ''}{restaurant.state ? `, ${restaurant.state}` : ''}</p>
          </div>
        )}
        {restaurant.contact_phone && (
          <div className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Contact</p>
            <p className="text-sm text-gray-700">📞 {restaurant.contact_phone}</p>
          </div>
        )}
        {restaurant.hours && (
          <div className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Hours</p>
            <p className="text-sm text-gray-700">🕐 {restaurant.hours}</p>
          </div>
        )}
        {restaurant.pricing_tier && (
          <div className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Price</p>
            <p className="text-sm text-gray-700">{restaurant.pricing_tier}</p>
          </div>
        )}
        {restaurant.amenities && (
          <div className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Amenities</p>
            <p className="text-sm text-gray-700">{restaurant.amenities}</p>
          </div>
        )}
        {restaurant.description && (
          <div className="bg-white rounded-xl border border-gray-100 p-4 sm:col-span-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">About</p>
            <p className="text-sm text-gray-700 leading-relaxed">{restaurant.description}</p>
          </div>
        )}
      </div>

      {/* Write Review Form */}
      {showReviewForm && isUser && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-8 fade-in shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Write a Review</h3>
          <form onSubmit={handleSubmitReview} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Your Rating</label>
              <StarRating value={newRating} onChange={setNewRating} size="lg" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Your Review</label>
              <textarea value={newComment} onChange={(e) => setNewComment(e.target.value)} required rows={4}
                placeholder="Share your experience..."
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-200 resize-none" />
            </div>
            {reviewError && <p className="text-red-500 text-sm">{reviewError}</p>}
            <div className="flex gap-3">
              <button type="submit" disabled={reviewLoading}
                className="px-6 py-2.5 bg-red-600 text-white font-medium rounded-xl text-sm hover:bg-red-700 disabled:opacity-50 transition-colors">
                {reviewLoading ? 'Submitting...' : 'Submit Review'}
              </button>
              <button type="button" onClick={() => setShowReviewForm(false)} className="px-6 py-2.5 text-gray-500 hover:text-gray-700 text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reviews */}
      <div>
        <h2 className="font-semibold text-gray-900 text-lg mb-4">Reviews ({reviews.length})</h2>
        {reviews.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-gray-100">
            <span className="text-4xl">💬</span>
            <p className="text-gray-500 mt-3 font-medium">No reviews yet</p>
            <p className="text-sm text-gray-400 mt-1">Be the first to review this restaurant!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {reviews.map((r) => {
              const isMyReview = currentUserId && String(r.user_id) === currentUserId
              const isEditing = editingReviewId === r.review_id

              return (
                <div key={r.review_id} className="bg-white rounded-xl border border-gray-100 p-5 fade-in">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-red-100 rounded-full flex items-center justify-center">
                        <span className="text-red-600 font-semibold text-sm">{r.user_name?.[0]?.toUpperCase() || 'U'}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">{r.user_name || 'Anonymous'}</p>
                        <p className="text-xs text-gray-400">{formatDate(r.created_at)}</p>
                      </div>
                    </div>
                    {isMyReview && !isEditing && (
                      <div className="flex gap-2">
                        <button onClick={() => { setEditingReviewId(r.review_id); setEditRating(r.rating); setEditComment(r.comment) }}
                          className="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded hover:bg-blue-50 transition-colors">Edit</button>
                        <button onClick={() => handleDeleteReview(r.review_id)}
                          className="text-xs text-red-500 hover:text-red-700 px-2 py-1 rounded hover:bg-red-50 transition-colors">Delete</button>
                      </div>
                    )}
                  </div>

                  {isEditing ? (
                    <div className="space-y-3">
                      <StarRating value={editRating} onChange={setEditRating} size="lg" />
                      <textarea value={editComment} onChange={(e) => setEditComment(e.target.value)} rows={3}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-200 resize-none" />
                      <div className="flex gap-2">
                        <button onClick={() => handleEditSave(r.review_id)}
                          className="px-4 py-1.5 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors">Save</button>
                        <button onClick={() => setEditingReviewId(null)}
                          className="px-4 py-1.5 text-gray-500 text-sm hover:text-gray-700">Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-1 mb-2">
                        {[1,2,3,4,5].map(s => (
                          <span key={s} style={{ color: s <= r.rating ? '#f5a623' : '#d1d5db' }}>★</span>
                        ))}
                      </div>
                      <p className="text-sm text-gray-700 leading-relaxed">{r.comment}</p>
                    </>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
