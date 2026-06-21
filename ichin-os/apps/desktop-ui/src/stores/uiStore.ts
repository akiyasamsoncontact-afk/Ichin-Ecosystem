import { create } from 'zustand'
import type { UIState, LayoutConfig } from '../types'

interface UIStore extends UIState {
  setActivePanel: (panel: string | null) => void
  setAmbientMode: (mode: UIState['ambientMode']) => void
  setLayout: (layout: Partial<LayoutConfig>) => void
  completeOnboarding: () => void
  setSpotlightOpen: (v: boolean) => void
  setCouncilOpen: (v: boolean) => void
  setMissionControlOpen: (v: boolean) => void
  setSettingsOpen: (v: boolean) => void
  setCheatsheetOpen: (v: boolean) => void
}

const DEFAULT_LAYOUT: LayoutConfig = {
  sidebarExpanded: false,
  panelPositions: {},
  panelSizes: {},
}

export const useUIStore = create<UIStore>((set) => ({
  activePanel: null,
  spotlightOpen: false,
  councilOpen: false,
  missionControlOpen: false,
  settingsOpen: false,
  cheatsheetOpen: false,
  ambientMode: 'neutral',
  layout: DEFAULT_LAYOUT,
  onboardingComplete: localStorage.getItem('ichin-onboarding') === 'complete',

  setActivePanel: (panel) => set({ activePanel: panel }),
  setAmbientMode: (mode) => set({ ambientMode: mode }),
  setLayout: (layout) =>
    set((s) => ({ layout: { ...s.layout, ...layout } })),
  completeOnboarding: () => {
    localStorage.setItem('ichin-onboarding', 'complete')
    set({ onboardingComplete: true })
  },
  setSpotlightOpen: (v) => set({ spotlightOpen: v }),
  setCouncilOpen: (v) => set({ councilOpen: v }),
  setMissionControlOpen: (v) => set({ missionControlOpen: v }),
  setSettingsOpen: (v) => set({ settingsOpen: v }),
  setCheatsheetOpen: (v) => set({ cheatsheetOpen: v }),
}))
