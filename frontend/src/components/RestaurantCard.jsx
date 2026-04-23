import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
<<<<<<< HEAD
import { addFavourite, removeFavourite } from '../services/api'
=======
import { uploadPath } from '../utils/mediaUrl'
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea

const CUISINE_COLORS = {
  Italian: ['#FEF3E2', '#B45309'], Chinese: ['#FEE2E2', '#B91C1C'],
  Mexican: ['#FEF9C3', '#92400E'], Indian: ['#FFF7ED', '#C2410C'],
  Japanese: ['#FCE7F3', '#9D174D'], American: ['#EFF6FF', '#1D4ED8'],
  French: ['#F5F3FF', '#6D28D9'], Mediterranean: ['#ECFDF5', '#065F46'],
  Thai: ['#FFF1F2', '#9F1239'], Korean: ['#F0FDF4', '#15803D'],
  Vietnamese: ['#FFF7ED', '#9A3412'], Greek: ['#EFF6FF', '#1E40AF'],
  Ethiopian: ['#FEF3C7', '#92400E'], Afghan: ['#F0FDF4', '#166534'],
  Portuguese: ['#EFF6FF', '#1E40AF'], Spanish: ['#FEF9C3', '#854D0E'],
  Burmese: ['#FFF1F2', '#9F1239'], Hawaiian: ['#ECFDF5', '#065F46'],
  Australian: ['#F0F9FF', '#0369A1'], Turkish: ['#FFF7ED', '#C2410C'],
}

const CUISINE_PHOTOS = {
  Italian: 'https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=600&q=80',
  Chinese: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&q=80',
  Mexican: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600&q=80',
  Indian: 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&q=80',
  Japanese: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600&q=80',
  American: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80',
  French: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80',
  Mediterranean: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80',
  Thai: 'https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=600&q=80',
  Korean: 'https://images.unsplash.com/photo-1583032015879-e5022cb87c3b?w=600&q=80',
  Vietnamese: 'https://images.unsplash.com/photo-1628689469838-524a4a973b8e?w=600&q=80',
  Greek: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&q=80',
  Spanish: 'https://images.unsplash.com/photo-1515443961218-a51367888e4b?w=600&q=80',
  Ethiopian: 'https://images.unsplash.com/photo-1567529692333-de9fd6772897?w=600&q=80',
  Afghan: 'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=600&q=80',
  Portuguese: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80',
  Burmese: 'https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=600&q=80',
  Hawaiian: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80',
  Australian: 'https://images.unsplash.com/photo-1529543544282-ea669407fca3?w=600&q=80',
  Turkish: 'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=600&q=80',
}
const DEFAULT_PHOTO = 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80'

function StarDisplay({ rating, count }) {
  const filled = Math.round(rating)
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex">
        {[1,2,3,4,5].map(s => (
          <span key={s} style={{ fontSize: 13, color: s <= filled ? '#C9942A' : '#DDD3C4' }}>★</span>
        ))}
      </div>
      <span style={{ fontSize: 13, color: 'var(--muted)', fontWeight: 500 }}>
        {rating > 0 ? rating.toFixed(1) : 'New'}
      </span>
      {count > 0 && <span style={{ fontSize: 12, color: '#B0A090' }}>({count})</span>}
    </div>
  )
}

<<<<<<< HEAD
export default function RestaurantCard({ restaurant, isFav = false, onFavToggle }) {
  const { user, isUser } = useAuth()
  const [fav, setFav] = useState(isFav)
  const [favLoading, setFavLoading] = useState(false)
=======
export default function RestaurantCard({
  restaurant,
  isFav = false,
  onFavToggle,
  favLoading: externalFavLoading = false,
}) {
  const { user, isUser } = useAuth()
  const [isTogglingFav, setIsTogglingFav] = useState(false)
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea
  const [imgError, setImgError] = useState(false)

  const colors = CUISINE_COLORS[restaurant.cuisine] || ['#F5F0E8', '#5C4A2A']
  const photo = restaurant.photos?.[0] || restaurant.photo
  const cuisinePhoto = CUISINE_PHOTOS[restaurant.cuisine] || DEFAULT_PHOTO
  const displayPhoto = (photo && !imgError)
<<<<<<< HEAD
    ? `http://localhost:8000/uploads/${photo}`
=======
    ? uploadPath(photo)
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea
    : cuisinePhoto

  const handleFav = async (e) => {
    e.preventDefault(); e.stopPropagation()
    if (!user || !isUser) return
<<<<<<< HEAD
    setFavLoading(true)
    try {
      if (fav) await removeFavourite(restaurant.id)
      else await addFavourite(restaurant.id)
      setFav(!fav)
      onFavToggle && onFavToggle(restaurant.id, !fav)
    } catch {}
    setFavLoading(false)
  }
=======
    if (externalFavLoading || isTogglingFav) return
    setIsTogglingFav(true)
    try {
      onFavToggle && (await onFavToggle(restaurant.id, !isFav))
    } catch {}
    setIsTogglingFav(false)
  }
  const effectiveFavLoading = externalFavLoading || isTogglingFav
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea

  return (
    <Link to={`/restaurants/${restaurant.id}`} className="block group">
      <div className="card overflow-hidden h-full">
        <div className="relative h-48 overflow-hidden" style={{ background: colors[0] }}>
          <img src={displayPhoto} alt={restaurant.name}
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          {isUser && (
<<<<<<< HEAD
            <button onClick={handleFav} disabled={favLoading}
              className={`absolute top-3 right-3 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200 shadow-sm ${fav ? 'bg-[#E8321A] text-white' : 'bg-white/90 backdrop-blur-sm text-[#8C7E6E] hover:text-[#E8321A] hover:scale-110'}`}>
              <span style={{ fontSize: 15 }}>{fav ? '♥' : '♡'}</span>
=======
            <button onClick={handleFav} disabled={effectiveFavLoading}
              className={`absolute top-3 right-3 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200 shadow-sm ${isFav ? 'bg-[#E8321A] text-white' : 'bg-white/90 backdrop-blur-sm text-[#8C7E6E] hover:text-[#E8321A] hover:scale-110'} ${effectiveFavLoading ? 'opacity-70' : ''}`}>
              <span style={{ fontSize: 15 }}>{isFav ? '♥' : '♡'}</span>
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea
            </button>
          )}
          <div className="absolute bottom-3 left-3">
            <span className="tag" style={{ background: colors[0], color: colors[1] }}>
              {restaurant.cuisine}
            </span>
          </div>
        </div>
        <div className="p-4">
          <h3 className="font-semibold text-[#1A1208] text-base mb-1.5 leading-snug truncate group-hover:text-[#E8321A] transition-colors duration-200">
            {restaurant.name}
          </h3>
          <StarDisplay rating={restaurant.avg_rating || 0} count={restaurant.review_count || 0} />
          <div className="flex items-center gap-2 mt-2">
            {restaurant.city && <span style={{ fontSize: 12, color: 'var(--muted)' }}>📍 {restaurant.city}</span>}
            {restaurant.pricing_tier && (
              <span style={{ fontSize: 12, fontWeight: 600, marginLeft: 'auto' }}
                className={restaurant.pricing_tier === '$' ? 'price-1' : restaurant.pricing_tier === '$$' ? 'price-2' : restaurant.pricing_tier === '$$$' ? 'price-3' : 'price-4'}>
                {restaurant.pricing_tier}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
