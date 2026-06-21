import { useEffect, useRef } from 'react'
import { useOrbStore } from '../stores/orbStore'
import { ORB_COLORS } from '../types'

export default function AIOrb() {
  const state = useOrbStore((s) => s.state)
  const notifications = useOrbStore((s) => s.notifications)
  const dismissNotification = useOrbStore((s) => s.dismissNotification)
  const countdown = useOrbStore((s) => s.countdown)
  const setCountdown = useOrbStore((s) => s.setCountdown)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const colors = ORB_COLORS[state]

  useEffect(() => {
    if (state === 'idle' && notifications.length === 0) {
      if (intervalRef.current) clearInterval(intervalRef.current)
      setCountdown(30)
      return
    }
    intervalRef.current = setInterval(() => {
      setCountdown(Math.max(0, useOrbStore.getState().countdown - 1))
    }, 1000)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [state, notifications.length])

  useEffect(() => {
    if (countdown <= 0 && notifications.length > 0) {
      notifications.forEach((n) => dismissNotification(n.id))
      setCountdown(30)
    }
  }, [countdown])

  const radius = 14
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - countdown / 30)

  return (
    <div style={{ position: 'fixed', top: 52, right: 16, zIndex: 40, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
      {notifications.map((n) => (
        <div
          key={n.id}
          style={{
            background: 'rgba(255,255,255,0.08)',
            backdropFilter: 'blur(20px)',
            borderRadius: 16,
            padding: 16,
            minWidth: 260,
            maxWidth: 320,
            border: '1px solid rgba(255,255,255,0.12)',
          }}
        >
          <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', marginBottom: 10 }}>{n.message}</p>
          <div style={{ display: 'flex', gap: 6 }}>
            {n.actions.map((a) => (
              <button
                key={a.action}
                onClick={() => { if (a.action === 'dismiss') dismissNotification(n.id) }}
                style={{
                  padding: '4px 12px',
                  borderRadius: 8,
                  fontSize: 10,
                  background: 'rgba(255,255,255,0.1)',
                  border: 'none',
                  color: 'rgba(255,255,255,0.7)',
                  cursor: 'pointer',
                }}
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>
      ))}

      <button
        style={{
          position: 'relative',
          width: 44,
          height: 44,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          border: 'none',
          background: colors.main + '20',
          boxShadow: `0 0 20px ${colors.glow}, 0 0 40px ${colors.glow}`,
          transition: 'box-shadow 0.3s ease',
        }}
      >
        <div style={{
          width: 22,
          height: 22,
          borderRadius: '50%',
          backgroundColor: colors.main,
          boxShadow: `0 0 12px ${colors.glow}`,
        }} />
        {state !== 'idle' && (
          <svg width="44" height="44" viewBox="0 0 44 44" style={{ position: 'absolute', top: 0, left: 0 }}>
            <circle cx="22" cy="22" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
            <circle
              cx="22" cy="22" r={radius}
              fill="none"
              stroke={colors.main}
              strokeWidth="2"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              transform="rotate(-90 22 22)"
              style={{ transition: 'stroke-dashoffset 1s linear' }}
            />
          </svg>
        )}
      </button>
    </div>
  )
}
