export default function StarRating({ value = 0, onChange, size = 'md', readOnly = false }) {
  const sizes = { sm: 16, md: 22, lg: 32 }
  const px = sizes[size] || 22

  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(star => (
        <span key={star}
          className={readOnly ? '' : 'star-interactive'}
          style={{
            fontSize: px,
            color: star <= value ? '#C9942A' : '#DDD3C4',
            cursor: readOnly ? 'default' : 'pointer',
            display: 'inline-block',
            lineHeight: 1,
          }}
          onClick={() => !readOnly && onChange && onChange(star)}
          onMouseEnter={e => !readOnly && (e.target.style.color = '#C9942A')}
          onMouseLeave={e => !readOnly && (e.target.style.color = star <= value ? '#C9942A' : '#DDD3C4')}
        >★</span>
      ))}
      {readOnly && value > 0 && (
        <span style={{ fontSize: 13, color: 'var(--muted)', marginLeft: 4, fontWeight: 500 }}>
          {value.toFixed(1)}
        </span>
      )}
    </div>
  )
}
