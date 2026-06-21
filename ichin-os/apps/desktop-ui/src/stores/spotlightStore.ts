import { create } from 'zustand'

interface SpotlightState {
  isOpen: boolean
  query: string
  open: () => void
  close: () => void
  setQuery: (q: string) => void
}

export const useSpotlightStore = create<SpotlightState>((set) => ({
  isOpen: false,
  query: '',
  open: () => set({ isOpen: true, query: '' }),
  close: () => set({ isOpen: false, query: '' }),
  setQuery: (q) => set({ query: q }),
}))
