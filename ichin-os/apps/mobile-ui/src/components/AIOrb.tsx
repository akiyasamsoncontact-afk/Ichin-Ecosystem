import { useEffect, useRef } from 'react'
import { View, Text, TouchableOpacity, StyleSheet, Animated } from 'react-native'
import { useOrbStore } from '../stores/orbStore'
import { ORB_COLORS } from '../types'

export default function AIOrb() {
  const state = useOrbStore((s) => s.state)
  const notifications = useOrbStore((s) => s.notifications)
  const dismissNotification = useOrbStore((s) => s.dismissNotification)
  const countdown = useOrbStore((s) => s.countdown)
  const setCountdown = useOrbStore((s) => s.setCountdown)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const pulseAnim = useRef(new Animated.Value(1)).current

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

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.15, duration: 1500, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 1500, useNativeDriver: true }),
      ])
    ).start()
  }, [state])

  const radius = 14
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - countdown / 30)

  return (
    <View style={styles.container}>
      {notifications.map((n) => (
        <View key={n.id} style={styles.notification}>
          <Text style={styles.notifText}>{n.message}</Text>
          <View style={styles.notifActions}>
            {n.actions.map((a) => (
              <TouchableOpacity
                key={a.action}
                onPress={() => { if (a.action === 'dismiss') dismissNotification(n.id) }}
                style={styles.notifBtn}
              >
                <Text style={styles.notifBtnText}>{a.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      ))}

      <TouchableOpacity style={styles.orb}>
        <Animated.View
          style={[
            styles.orbInner,
            {
              backgroundColor: colors.main + '20',
              shadowColor: colors.main,
              shadowOpacity: 0.4,
              shadowRadius: 20,
              transform: [{ scale: pulseAnim }],
            },
          ]}
        >
          <View style={[styles.orbDot, { backgroundColor: colors.main }]} />
        </Animated.View>
        {state !== 'idle' && (
          <View style={styles.countdownOverlay}>
            <Text style={styles.countdownText}>{countdown}</Text>
          </View>
        )}
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 80,
    right: 16,
    alignItems: 'flex-end',
    zIndex: 100,
  },
  notification: {
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    minWidth: 200,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.12)',
  },
  notifText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 8,
  },
  notifActions: {
    flexDirection: 'row',
    gap: 6,
  },
  notifBtn: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  notifBtnText: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.7)',
  },
  orb: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  orbInner: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  orbDot: {
    width: 24,
    height: 24,
    borderRadius: 12,
  },
  countdownOverlay: {
    position: 'absolute',
    bottom: -4,
    right: -4,
    backgroundColor: '#0A0A0A',
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  countdownText: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.6)',
    fontFamily: 'monospace',
  },
})
