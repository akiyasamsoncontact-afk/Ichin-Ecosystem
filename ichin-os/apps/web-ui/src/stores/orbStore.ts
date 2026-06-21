import { create } from 'zustand'
import type { OrbState, OrbNotification } from '../types'

interface OrbStore {
  state: OrbState
  notifications: OrbNotification[]
  setState: (s: OrbState) => void
  addNotification: (n: OrbNotification) => void
  dismissNotification: (id: string) => void
  countdown: number
  setCountdown: (n: number) => void
}

export const useOrbStore = create<OrbStore>((set) => ({
  state: 'idle',
  notifications: [],
  countdown: 30,
  setState: (state) => set({ state }),
  addNotification: (n) =>
    set((s) => ({ notifications: [...s.notifications, n], state: n.state })),
  dismissNotification: (id) =>
    set((s) => ({
      notifications: s.notifications.filter((x) => x.id !== id),
      state: s.notifications.length <= 1 ? 'idle' : s.state,
    })),
  setCountdown: (countdown) => set({ countdown }),
}))
