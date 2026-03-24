import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { chatWithAI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const QUICK_ACTIONS = [
  { icon: '🍽', label: 'Dinner tonight', msg: "I'm looking for a great place for dinner tonight" },
  { icon: '⭐', label: 'Best rated', msg: 'Show me the highest rated restaurants' },
  { icon: '🥗', label: 'Vegan options', msg: "I'm vegan, what are my best casual options?" },
  { icon: '💑', label: 'Romantic dinner', msg: 'Something romantic for a special occasion' },
  { icon: '🍜', label: 'Asian food', msg: 'I want authentic Asian food' },
  { icon: '💰', label: 'Budget friendly', msg: 'Show me good affordable restaurants' },
]

function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/gs, '$1')
    .replace(/\*(.+?)\*/gs, '$1')
    .replace(/_(.+?)_/gs, '$1')
    .replace(/`(.+?)`/g, '$1')
    .replace(/^#{1,3}\s+/gm, '')
    .replace(/^[•\-\*]\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    .replace(/💡[^\n]*/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
    .replace(/\n/g, '<br/>')
}

function TypingIndicator() {
  return (
    <div className="flex gap-1.5 items-center px-4 py-3">
      {[0,1,2].map(i => (
        <span key={i} className="typing-dot"
          style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--muted)', display: 'inline-block', animationDelay: `${i*0.2}s` }} />
      ))}
    </div>
  )
}

function RestaurantRecommendation({ r }) {
  const stars = Math.round(r.rating || r.avg_rating || 0)
  return (
    <Link to={`/restaurants/${r.id}`}
      className="group flex items-center gap-3 p-3 rounded-xl border transition-all duration-200"
      style={{ borderColor: 'rgba(26,18,8,0.07)', background: 'rgba(253,248,243,0.6)' }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(232,50,26,0.25)'; e.currentTarget.style.background = 'rgba(232,50,26,0.04)' }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(26,18,8,0.07)'; e.currentTarget.style.background = 'rgba(253,248,243,0.6)' }}>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 font-semibold text-white text-sm"
        style={{ background: 'var(--red)', fontFamily: "'Fraunces', serif" }}>
        {r.name?.[0]?.toUpperCase() || '🍴'}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-[#1A1208] truncate group-hover:text-[#E8321A] transition-colors" style={{ fontSize: 13 }}>
          {r.name}
        </p>
        <div className="flex items-center gap-1.5">
          <span style={{ color: '#C9942A', fontSize: 11 }}>{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
          {(r.price || r.pricing_tier) && <span style={{ fontSize: 11, color: 'var(--muted)' }}>· {r.price || r.pricing_tier}</span>}
          {r.cuisine && <span style={{ fontSize: 11, color: 'var(--muted)' }}>· {r.cuisine}</span>}
        </div>
        {r.reason && <p style={{ fontSize: 11, color: 'var(--muted)', marginTop: 1, fontStyle: 'italic' }}>{r.reason}</p>}
      </div>
      <span style={{ fontSize: 14, color: '#DDD3C4', flexShrink: 0 }} className="group-hover:text-[#E8321A] transition-colors">›</span>
    </Link>
  )
}

export default function ChatbotPanel() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([{
    role: 'assistant',
    content: "Hi! I'm your AI restaurant assistant. Tell me what you're craving, the occasion, or your preferences — and I'll find the perfect spot for you.",
    recs: [],
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return
    setInput('')

    const updatedMessages = [...messages, { role: 'user', content: msg }]
    setMessages(updatedMessages)
    setLoading(true)

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }))
      const res = await chatWithAI({ message: msg, conversation_history: history })
      const { response, recommended_restaurants } = res.data
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response,
        recs: recommended_restaurants || [],
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I couldn't connect right now. Please make sure the backend is running and try again.",
        recs: [],
        isError: true,
      }])
    }
    setLoading(false)
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  const clearChat = () => setMessages([{
    role: 'assistant',
    content: "Chat cleared! What are you looking for today?",
    recs: [],
  }])

  const showQuickActions = messages.length <= 1

  return (
    <div className="flex flex-col h-full rounded-2xl overflow-hidden bg-white"
      style={{ border: '1px solid rgba(26,18,8,0.08)', boxShadow: '0 4px 24px rgba(26,18,8,0.06)' }}>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3.5 flex-shrink-0"
        style={{ background: 'var(--ink)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'var(--red)' }}>
              <span style={{ fontSize: 16 }}>🤖</span>
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2"
              style={{ background: '#22C55E', borderColor: 'var(--ink)' }} />
          </div>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: 'white', lineHeight: 1.2 }}>AI Restaurant Assistant</p>
            <p style={{ fontSize: 11, color: 'rgba(253,248,243,0.45)', marginTop: 1 }}>
              {loading ? 'Thinking...' : 'Powered by your preferences'}
            </p>
          </div>
        </div>
        <button onClick={clearChat} style={{ fontSize: 11, color: 'rgba(253,248,243,0.35)', fontWeight: 500, padding: '4px 8px', borderRadius: 6 }}
          onMouseEnter={e => e.target.style.color = 'rgba(253,248,243,0.8)'}
          onMouseLeave={e => e.target.style.color = 'rgba(253,248,243,0.35)'}>
          Clear chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto min-h-0 p-4 space-y-4"
        style={{ background: '#F9F7F4', scrollbarWidth: 'thin', scrollbarColor: 'rgba(26,18,8,0.1) transparent' }}>
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in`}>
            <div className={msg.role === 'user' ? 'max-w-[80%]' : 'max-w-[92%] w-full'}>
              {msg.role === 'assistant' && (
                <div className="flex items-center gap-1.5 mb-1.5">
                  <div className="w-5 h-5 rounded-lg flex items-center justify-center" style={{ background: 'var(--red)' }}>
                    <span style={{ fontSize: 10 }}>🤖</span>
                  </div>
                  <span style={{ fontSize: 11, color: 'var(--muted)', fontWeight: 500 }}>Assistant</span>
                </div>
              )}
              <div className={msg.role === 'user' ? 'bubble-user' : 'bubble-ai'}
                style={msg.isError ? { borderColor: 'rgba(232,50,26,0.2)', background: 'rgba(232,50,26,0.04)' } : {}}>
                <p style={{ lineHeight: 1.6 }}
                  dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }} />
              </div>
              {msg.recs && msg.recs.length > 0 && (
                <div className="mt-2 space-y-2">
                  <p style={{ fontSize: 11, color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', paddingLeft: 2, marginTop: 4 }}>
                    Recommended for you
                  </p>
                  {msg.recs.map((r, j) => <RestaurantRecommendation key={j} r={r} />)}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start fade-in">
            <div>
              <div className="flex items-center gap-1.5 mb-1.5">
                <div className="w-5 h-5 rounded-lg flex items-center justify-center" style={{ background: 'var(--red)' }}>
                  <span style={{ fontSize: 10 }}>🤖</span>
                </div>
                <span style={{ fontSize: 11, color: 'var(--muted)', fontWeight: 500 }}>Thinking...</span>
              </div>
              <div className="bubble-ai"><TypingIndicator /></div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick actions */}
      {showQuickActions && (
        <div className="px-3 py-2.5 flex-shrink-0"
          style={{ background: '#F9F7F4', borderTop: '1px solid rgba(26,18,8,0.04)' }}>
          <p style={{ fontSize: 10, fontWeight: 600, color: 'var(--muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8, paddingLeft: 2 }}>
            Quick suggestions
          </p>
          <div className="flex flex-wrap gap-1.5">
            {QUICK_ACTIONS.map(q => (
              <button key={q.label} onClick={() => sendMessage(q.msg)}
                style={{ padding: '5px 12px', borderRadius: 99, fontSize: 12, fontWeight: 500, color: 'var(--ink-soft)', background: 'white', border: '1px solid rgba(26,18,8,0.1)', cursor: 'pointer' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(232,50,26,0.3)'; e.currentTarget.style.color = 'var(--red)'; e.currentTarget.style.background = 'rgba(232,50,26,0.04)' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(26,18,8,0.1)'; e.currentTarget.style.color = 'var(--ink-soft)'; e.currentTarget.style.background = 'white' }}>
                <span style={{ fontSize: 13 }}>{q.icon}</span> {q.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {!user && (
        <div className="px-4 py-2.5 flex-shrink-0 text-center" style={{ background: '#FFFBF5', borderTop: '1px solid rgba(201,148,42,0.15)' }}>
          <p style={{ fontSize: 12, color: 'var(--muted)' }}>
            <Link to="/login" style={{ color: 'var(--red)', fontWeight: 600 }} className="hover:underline">Log in</Link>
            {' '}for personalized AI recommendations
          </p>
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 flex-shrink-0 bg-white" style={{ borderTop: '1px solid rgba(26,18,8,0.07)' }}>
        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea ref={inputRef} value={input}
              onChange={e => { setInput(e.target.value); e.target.style.height = 'auto'; e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px' }}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
              placeholder="Ask about restaurants, cuisine, occasion..."
              rows={1} className="input-field resize-none rounded-xl pr-3"
              style={{ paddingTop: 10, paddingBottom: 10, fontSize: 14, lineHeight: 1.5, minHeight: 42, maxHeight: 100 }} />
          </div>
          <button onClick={() => sendMessage()} disabled={loading || !input.trim()}
            className="btn-primary rounded-xl flex-shrink-0 disabled:opacity-40"
            style={{ padding: '10px 18px', fontSize: 14, minHeight: 42 }}>
            {loading ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full inline-block"
                style={{ animation: 'spin 0.8s linear infinite' }} />
            ) : '↑'}
          </button>
        </div>
        <p style={{ fontSize: 11, color: 'rgba(140,126,110,0.6)', marginTop: 6, textAlign: 'center' }}>
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
