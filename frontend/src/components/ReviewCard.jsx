import { useState } from 'react'
import StarRating from './StarRating'
import { updateReview, deleteReview } from '../services/api'

export default function ReviewCard({ review, currentUserId, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false)
  const [rating, setRating] = useState(review.rating)
  const [comment, setComment] = useState(review.comment)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isOwner = String(review.user_id) === String(currentUserId)
  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

  const handleSave = async () => {
    setLoading(true); setError('')
    try {
      const res = await updateReview(review.review_id, { rating, comment })
      onUpdate && onUpdate({ ...review, rating, comment })
      setEditing(false)
    } catch (e) { setError(e.response?.data?.detail || 'Failed to update') }
    setLoading(false)
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this review?')) return
    setLoading(true)
    try { await deleteReview(review.review_id); onDelete && onDelete(review.review_id) }
    catch (e) { setError(e.response?.data?.detail || 'Failed to delete') }
    setLoading(false)
  }

  return (
    <div className="card p-5 fade-in" style={{ boxShadow: 'none', border: '1px solid var(--border)' }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center font-semibold text-white shadow-sm"
            style={{ background: `hsl(${(review.user_name?.charCodeAt(0) || 0) * 15 % 360}, 60%, 45%)`, fontSize: 14 }}>
            {review.user_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <p className="font-semibold text-[#1A1208]" style={{ fontSize: 14 }}>{review.user_name || 'Anonymous'}</p>
            <p style={{ fontSize: 12, color: 'var(--muted)' }}>{formatDate(review.created_at || review.date)}</p>
          </div>
        </div>
        {isOwner && !editing && (
          <div className="flex gap-1">
            <button onClick={() => setEditing(true)}
              className="px-3 py-1 rounded-lg hover:bg-blue-50 transition-colors"
              style={{ fontSize: 12, color: '#3B82F6', fontWeight: 500 }}>
              Edit
            </button>
            <button onClick={handleDelete} disabled={loading}
              className="px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
              style={{ fontSize: 12, color: 'var(--red)', fontWeight: 500 }}>
              Delete
            </button>
          </div>
        )}
      </div>

      {editing ? (
        <div className="space-y-3">
          <StarRating value={rating} onChange={setRating} size="lg" />
          <textarea value={comment} onChange={e => setComment(e.target.value)}
            rows={3} className="input-field resize-none" />
          {error && <p style={{ fontSize: 12, color: 'var(--red)' }}>{error}</p>}
          <div className="flex gap-2">
            <button onClick={handleSave} disabled={loading} className="btn-primary text-sm px-4 py-2 rounded-lg">
              {loading ? 'Saving...' : 'Save'}
            </button>
            <button onClick={() => setEditing(false)} className="btn-ghost text-sm px-4 py-2 rounded-lg">Cancel</button>
          </div>
        </div>
      ) : (
        <>
          <StarRating value={review.rating} readOnly size="sm" />
          <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, marginTop: 8 }}>{review.comment}</p>
        </>
      )}
    </div>
  )
}
