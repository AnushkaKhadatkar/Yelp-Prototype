export default function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="spinner" />
      <p style={{ fontSize: 14, color: 'var(--muted)', fontWeight: 500 }}>{text}</p>
    </div>
  )
}

export function InlineSpinner() {
  return <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full" style={{ animation: 'spin 0.8s linear infinite' }} />
}
