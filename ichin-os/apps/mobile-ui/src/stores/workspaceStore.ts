import { create } from 'zustand'
import type { WorkspaceType } from '../types'

interface WorkspaceState {
  active: WorkspaceType
  setActive: (ws: WorkspaceType) => void
  cycle: () => void
}

const ORDER: WorkspaceType[] = ['study', 'coding', 'learning', 'personal']

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  active: 'study',
  setActive: (ws) => set({ active: ws }),
  cycle: () => {
    const current = get().active
    const idx = ORDER.indexOf(current)
    set({ active: ORDER[(idx + 1) % ORDER.length] })
  },
}))
