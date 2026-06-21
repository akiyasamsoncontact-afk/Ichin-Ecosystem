import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useOrbStore } from '../../stores/orbStore'

const STATE_COLORS = {
  idle: { main: '#4A9EFF', glow: 'rgba(74, 158, 255, 0.3)' },
  active: { main: '#00E676', glow: 'rgba(0, 230, 118, 0.3)' },
  critical: { main: '#FF5252', glow: 'rgba(255, 82, 82, 0.4)' },
}

function CountdownRing({ countdown, color }: { countdown: number; color: string }) {
  const radius = 14
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - countdown / 30)

  return (
    <svg width="36" height="36" viewBox="0 0 36 36" className="absolute">
      <circle cx="18" cy="18" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
      <circle
        cx="18" cy="18" r={radius}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 18 18)"
        style={{ transition: 'stroke-dashoffset 1s linear' }}
      />
    </svg>
  )
}

export default function AIOrb() {
  const state = useOrbStore((s) => s.state)
  const notifications = useOrbStore((s) => s.notifications)
  const dismissNotification = useOrbStore((s) => s.dismissNotification)
  const countdown = useOrbStore((s) => s.countdown)
  const setCountdown = useOrbStore((s) => s.setCountdown)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const colors = STATE_COLORS[state]

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

  return (
    <div className="fixed top-4 right-4 z-40 flex flex-col items-end gap-2">
      <AnimatePresence>
        {notifications.map((n) => (
          <motion.div
            key={n.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="glass-strong rounded-2xl p-4 min-w-[280px] max-w-sm"
          >
            <p className="text-sm text-white/80 mb-3">{n.message}</p>
            <div className="flex gap-2">
              {n.actions.map((a) => (
                <button
                  key={a.action}
                  onClick={() => {
                    if (a.action === 'dismiss') dismissNotification(n.id)
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs bg-white/10 text-white/70 hover:bg-white/15 transition-all"
                >
                  {a.label}
                </button>
              ))}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      <motion.button
        className="relative w-12 h-12 rounded-full flex items-center justify-center cursor-pointer"
        animate={{
          boxShadow: `0 0 20px ${colors.glow}, 0 0 40px ${colors.glow}`,
        }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        style={{ backgroundColor: colors.main + '20' }}
      >
        <div
          className="w-6 h-6 rounded-full"
          style={{ backgroundColor: colors.main, boxShadow: `0 0 12px ${colors.glow}` }}
        />
        {state !== 'idle' && (
          <CountdownRing countdown={countdown} color={colors.main} />
        )}
      </motion.button>
    </div>
  )
}
