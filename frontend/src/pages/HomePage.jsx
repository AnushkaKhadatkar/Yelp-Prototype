import { useState, useEffect } from 'react'
import { getRestaurants, getFavourites } from '../services/api'
import { useAuth } from '../context/AuthContext'
import RestaurantCard from '../components/RestaurantCard'
import ChatbotPanel from '../components/ChatbotPanel'
import LoadingSpinner from '../components/LoadingSpinner'

const CUISINES = ['Italian','Chinese','Mexican','Indian','Japanese','American','French','Mediterranean','Thai','Korean']

function SkeletonCard() {
  return (
    <div className="card overflow-hidden">
      <div className="skeleton h-48 rounded-none" />
      <div className="p-4 space-y-2">
        <div className="skeleton h-5 w-3/4 rounded" />
        <div className="skeleton h-4 w-1/2 rounded" />
        <div className="skeleton h-3 w-1/3 rounded" />
      </div>
    </div>
  )
}

export default function HomePage() {
  const { user, isUser } = useAuth()
  const [restaurants, setRestaurants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [favIds, setFavIds] = useState(new Set())
  const [search, setSearch] = useState('')
  const [cuisine, setCuisine] = useState('')
  const [city, setCity] = useState('')
  const [keyword, setKeyword] = useState('')
  const [chatOpen, setChatOpen] = useState(false)
  const [activeFilter, setActiveFilter] = useState('All')

  const fetchRestaurants = async (params = {}) => {
    setLoading(true); setError('')
    try {
      const res = await getRestaurants(params)
      setRestaurants(res.data || [])
    } catch {
      setError('Could not connect to the server.')
    }
    setLoading(false)
  }

  const fetchFavs = async () => {
    if (!isUser) return
    try {
      const res = await getFavourites()
      setFavIds(new Set((res.data || []).map(r => r.id || r.restaurant_id)))
    } catch {}
  }

  useEffect(() => { fetchRestaurants(); fetchFavs() }, [user])

  const handleSearch = (e) => {
    e.preventDefault()
    const params = {}
    // Backend expects `search` (and/or `keyword`) for text search.
    // Keep `search` in sync with the main search box.
    if (search) params.search = search
    if (cuisine && cuisine !== 'All') params.cuisine = cuisine
    if (city) params.city = city
    if (keyword) params.keyword = keyword
    fetchRestaurants(params)
  }

  const handleCuisineFilter = (c) => {
    setActiveFilter(c)
    // Cuisine pills should *combine* with the current search inputs, not replace them.
    const params = {}
    if (search) params.search = search
    if (city) params.city = city
    if (keyword) params.keyword = keyword

    if (c === 'All') {
      setCuisine('')
    } else {
      setCuisine(c)
      params.cuisine = c
    }

    fetchRestaurants(params)
  }

  const handleFavToggle = (id, isFav) => {
    setFavIds(prev => {
      const next = new Set(prev)
      if (isFav) next.add(id); else next.delete(id)
      return next
    })
  }

  const clearFilters = () => {
    setSearch(''); setCity(''); setKeyword(''); setCuisine('')
    setActiveFilter('All'); fetchRestaurants()
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--cream)' }}>
      {/* ── Hero ── */}
      <div className="hero-gradient relative overflow-hidden">
        <div className="absolute -top-32 -right-32 w-[500px] h-[500px] rounded-full opacity-[0.04]"
          style={{ background: 'var(--red)' }} />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 rounded-full opacity-[0.03]"
          style={{ background: 'var(--gold)' }} />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
          <div className="max-w-xl">
            <p className="section-eyebrow mb-3 fade-up stagger-1">Find your next great meal</p>
            <h1 className="font-display text-5xl md:text-6xl text-white leading-[1.05] mb-4 fade-up stagger-2"
              style={{ letterSpacing: '-0.02em' }}>
              Discover<br />
              restaurants<br />
              <em className="text-[#E8321A] not-italic">you'll love</em>
            </h1>
            <p className="text-[rgba(253,248,243,0.55)] text-lg mb-10 fade-up stagger-3">
              Search, explore, and let our AI guide<br className="hidden sm:block" /> your next dining experience.
            </p>
          </div>

          {/* ── Search Card ── */}
          <form onSubmit={handleSearch}
            className="bg-white rounded-2xl p-4 shadow-2xl max-w-2xl fade-up stagger-4"
            style={{ boxShadow: '0 32px 80px rgba(0,0,0,0.4)' }}>

            {/* Row 1: name + city + button */}
            <div className="flex flex-col sm:flex-row gap-2 mb-2">
              <div className="flex-1 relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
                  style={{ fontSize: 15, color: '#8C7E6E', lineHeight: 1 }}>
                  🔍
                </span>
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Restaurant or cuisine..."
                  className="input-field rounded-xl"
                  style={{ paddingLeft: 38, paddingTop: 12, paddingBottom: 12 }}
                />
              </div>
              <div className="flex-1 relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
                  style={{ fontSize: 15, color: '#8C7E6E', lineHeight: 1 }}>
                  📍
                </span>
                <input
                  type="text"
                  value={city}
                  onChange={e => setCity(e.target.value)}
                  placeholder="City or neighborhood..."
                  className="input-field rounded-xl"
                  style={{ paddingLeft: 38, paddingTop: 12, paddingBottom: 12 }}
                />
              </div>
              <button type="submit" className="btn-primary px-7 py-3 rounded-xl whitespace-nowrap font-semibold">
                Search
              </button>
            </div>

            {/* Row 2: keyword + cuisine */}
            <div className="flex flex-col sm:flex-row gap-2 items-center">
              <div className="flex-1 w-full relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
                  style={{ fontSize: 13, color: '#8C7E6E', lineHeight: 1 }}>
                  🏷
                </span>
                <input
                  type="text"
                  value={keyword}
                  onChange={e => setKeyword(e.target.value)}
                  placeholder="Keywords: wifi, outdoor, romantic..."
                  className="input-field rounded-xl w-full"
                  style={{ paddingLeft: 34, paddingTop: 10, paddingBottom: 10, fontSize: 13 }}
                />
              </div>
              <div className="flex-shrink-0 w-full sm:w-44 relative">
                <select
                  value={cuisine}
                  onChange={e => setCuisine(e.target.value)}
                  className="input-field rounded-xl w-full appearance-none"
                  style={{ paddingTop: 10, paddingBottom: 10, paddingRight: 28, fontSize: 13, cursor: 'pointer' }}
                >
                  <option value="">All cuisines</option>
                  {CUISINES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <span className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
                  style={{ fontSize: 10, color: '#8C7E6E' }}>▼</span>
              </div>
              {(search || city || keyword || cuisine) && (
                <button type="button" onClick={clearFilters}
                  className="flex-shrink-0 px-3 py-2 rounded-xl transition-colors whitespace-nowrap"
                  style={{ fontSize: 13, color: '#8C7E6E', fontWeight: 500 }}
                  onMouseEnter={e => e.target.style.color = 'var(--red)'}
                  onMouseLeave={e => e.target.style.color = '#8C7E6E'}>
                  ✕ Clear
                </button>
              )}
            </div>
          </form>
        </div>
      </div>

      {/* ── Cuisine Pills ── */}
      <div className="border-b border-[rgba(26,18,8,0.06)] bg-white sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-2 overflow-x-auto py-3"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
            {['All', ...CUISINES].map(c => (
              <button key={c} onClick={() => handleCuisineFilter(c)}
                className="flex-shrink-0 transition-all duration-200"
                style={{
                  padding: '6px 16px',
                  borderRadius: 99,
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: 'pointer',
                  border: activeFilter === c ? 'none' : '1px solid rgba(26,18,8,0.1)',
                  background: activeFilter === c ? 'var(--red)' : 'white',
                  color: activeFilter === c ? 'white' : 'var(--ink-soft)',
                  boxShadow: activeFilter === c ? '0 4px 12px rgba(232,50,26,0.3)' : 'none',
                }}>
                {c}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Main content ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col gap-8">

          {/* Restaurant grid */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="font-display text-2xl font-semibold text-[#1A1208]" style={{ letterSpacing: '-0.01em' }}>
                  {loading ? 'Finding...' : `${restaurants.length} restaurant${restaurants.length !== 1 ? 's' : ''}`}
                </h2>
                {!loading && restaurants.length > 0 && (
                  <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 2 }}>
                    {activeFilter !== 'All' ? `Filtered by ${activeFilter}` : 'All restaurants'}
                  </p>
                )}
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                {[1,2,3,4,5,6].map(i => <SkeletonCard key={i} />)}
              </div>
            ) : error ? (
              <div className="text-center py-20">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-50 flex items-center justify-center">
                  <span style={{ fontSize: 28 }}>⚠️</span>
                </div>
                <p className="font-semibold text-[#1A1208] mb-2">Connection error</p>
                <p style={{ fontSize: 14, color: 'var(--muted)', marginBottom: 16 }}>{error}</p>
                <button className="btn-primary" onClick={() => fetchRestaurants()}>Try Again</button>
              </div>
            ) : restaurants.length === 0 ? (
              <div className="text-center py-24">
                <div className="w-20 h-20 mx-auto mb-5 rounded-2xl flex items-center justify-center"
                  style={{ background: 'rgba(232,50,26,0.07)' }}>
                  <span style={{ fontSize: 36 }}>🍽</span>
                </div>
                <p className="font-display text-xl font-semibold text-[#1A1208] mb-2">No restaurants found</p>
                <p style={{ fontSize: 14, color: 'var(--muted)', marginBottom: 20 }}>
                  Try adjusting your filters or search terms
                </p>
                <button className="btn-ghost" onClick={clearFilters}>Clear all filters</button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                {restaurants.map((r, i) => (
                  <div key={r.id} className="fade-up"
                    style={{ animationDelay: `${Math.min(i * 0.04, 0.3)}s`, opacity: 0 }}>
                    <RestaurantCard
                      restaurant={r}
                      isFav={favIds.has(r.id)}
                      onFavToggle={handleFavToggle}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Floating Chatbot Icon */}
      <button
        type="button"
        aria-label={chatOpen ? "Close AI assistant" : "Open AI assistant"}
        onClick={() => setChatOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-[60] rounded-full shadow-lg"
        style={{
          width: 56,
          height: 56,
          background: 'var(--red)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 22,
          boxShadow: '0 14px 34px rgba(232,50,26,0.35)',
        }}
      >
        🤖
      </button>

      {/* Chatbot Popover/Modal */}
      {chatOpen && (
        <div className="fixed inset-0 z-[70]">
          {/* Backdrop */}
          <div
            className="absolute inset-0"
            style={{ background: 'rgba(0,0,0,0.35)' }}
            onClick={() => setChatOpen(false)}
          />

          {/* Panel */}
          <div
            className="absolute bottom-6 right-6 w-[92vw] max-w-[420px] h-[70vh] max-h-[680px] scale-in"
            style={{ borderRadius: 16 }}
          >
            <ChatbotPanel />
          </div>
        </div>
      )}
    </div>
  )
}
