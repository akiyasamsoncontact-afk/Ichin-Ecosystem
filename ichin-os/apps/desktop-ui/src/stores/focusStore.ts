import { create } from 'zustand'
import type { FocusMode } from '../types'
import { uiApi } from '../services/api'

interface FocusState {
  mode: FocusMode
  blockedProcesses: string[]
  setMode: (mode: FocusMode) => Promise<void>
  cycleMode: () => Promise<void>
  loadFocusState: () => Promise<void>
}

const ORDER: FocusMode[] = ['normal', 'focus', 'deep_focus', 'lock']

export const useFocusStore = create<FocusState>((set, get) => ({
  mode: 'normal',
  blockedProcesses: [],
  setMode: async (mode) => {
    set({ mode })
    try { await uiApi.focus.setMode(mode) } catch { /* offline */ }
  },
  cycleMode: async () => {
    const current = get().mode
    const idx = ORDER.indexOf(current)
    const next = ORDER[(idx + 1) % ORDER.length]
    const blocked = next === 'lock'
      ? ['browser', 'games', 'social', 'entertainment']
      : []
    set({ mode: next, blockedProcesses: blocked })
    try { await uiApi.focus.setMode(next) } catch { /* offline */ }
  },
  loadFocusState: async () => {
    try {
      const state = await uiApi.focus.getState()
      set({ mode: state.mode, blockedProcesses: state.blockedProcesses })
    } catch { /* offline */ }
  },
}))
