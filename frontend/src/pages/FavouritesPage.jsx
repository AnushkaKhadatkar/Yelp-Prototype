<<<<<<< HEAD
import { useState, useEffect } from 'react'
import { getFavourites } from '../services/api'
import RestaurantCard from '../components/RestaurantCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { Link } from 'react-router-dom'

export default function FavouritesPage() {
  const [favourites, setFavourites] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getFavourites()
      .then(res => setFavourites(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleFavToggle = (id) => setFavourites(prev => prev.filter(r => (r.id || r.restaurant_id) !== id))
=======
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import RestaurantCard from '../components/RestaurantCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { Link } from 'react-router-dom'
import { fetchFavourites, optimisticRemoveFavourite, removeFavouriteItem } from '../slices/favouritesSlice'
import {
  selectFavouriteItems,
  selectFavouritesLoading,
  selectFavouritesPendingById,
} from '../selectors/favouritesSelectors'

export default function FavouritesPage() {
  const dispatch = useDispatch()
  const favourites = useSelector(selectFavouriteItems)
  const loading = useSelector(selectFavouritesLoading)
  const pendingById = useSelector(selectFavouritesPendingById)

  useEffect(() => {
    dispatch(fetchFavourites())
  }, [dispatch])

  const handleFavToggle = async (id) => {
    const rid = Number(id)
    dispatch(optimisticRemoveFavourite(rid))
    await dispatch(removeFavouriteItem(rid))
  }
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <p className="section-eyebrow mb-1">Your collection</p>
        <h1 className="font-display text-3xl font-semibold text-[#1A1208]">Saved Restaurants</h1>
      </div>

      {loading ? <LoadingSpinner text="Loading your saved places..." />
      : favourites.length === 0 ? (
        <div className="text-center py-24">
          <div className="w-20 h-20 mx-auto mb-5 rounded-2xl bg-red-50 flex items-center justify-center">
            <span style={{ fontSize: 36 }}>🤍</span>
          </div>
          <h2 className="font-display text-xl font-semibold text-[#1A1208] mb-2">No saved restaurants yet</h2>
          <p className="text-[#8C7E6E] mb-6">Heart a restaurant to save it here</p>
          <Link to="/" className="btn-primary">Explore Restaurants</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {favourites.map((r, i) => (
            <div key={r.id || r.restaurant_id} className="fade-up" style={{ animationDelay: `${i * 0.05}s`, opacity: 0 }}>
              <RestaurantCard
                restaurant={{ ...r, id: r.id || r.restaurant_id }}
                isFav={true}
<<<<<<< HEAD
=======
                favLoading={Boolean(pendingById[Number(r.id || r.restaurant_id)])}
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea
                onFavToggle={handleFavToggle}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
