import Shell from './components/Shell'
import Sidebar from './components/Sidebar'
import WorkspaceContainer from './components/WorkspaceContainer'
import AIOrb from './components/AIOrb'
import Spotlight from './components/Spotlight'
import AICouncil from './components/AICouncil'
import FocusOverlay from './components/FocusOverlay'
import MissionControl from './components/MissionControl'
import Settings from './components/Settings'
import { useUIStore } from './stores/uiStore'
import { useWorkspaceStore } from './stores/workspaceStore'
import { useFocusStore } from './stores/focusStore'
import { useEffect } from 'react'

export default function App() {
  const cycleWorkspace = useWorkspaceStore((s) => s.cycle)
  const cycleFocus = useFocusStore((s) => s.cycleMode)
  const loadFocusState = useFocusStore((s) => s.loadFocusState)
  const {
    setSpotlightOpen,
    setCouncilOpen,
    setMissionControlOpen,
    setSettingsOpen,
    setCheatsheetOpen,
  } = useUIStore()

  useEffect(() => {
    loadFocusState()
  }, [])

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const ctrl = e.ctrlKey || e.metaKey
      if (!ctrl) return
      switch (e.code) {
        case 'Space':
          e.preventDefault()
          setSpotlightOpen(true)
          break
        case 'KeyA':
          e.preventDefault()
          setCouncilOpen(true)
          break
        case 'KeyF':
          e.preventDefault()
          cycleFocus()
          break
        case 'Tab':
          e.preventDefault()
          cycleWorkspace()
          break
        case 'KeyW':
          if (e.shiftKey) {
            e.preventDefault()
            setMissionControlOpen(true)
          }
          break
        case 'Comma':
          e.preventDefault()
          setSettingsOpen(true)
          break
        case 'Slash':
          e.preventDefault()
          setCheatsheetOpen(true)
          break
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg)', color: 'var(--text)' }}>
      <Shell />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, overflow: 'auto' }}>
          <WorkspaceContainer />
        </main>
      </div>
      <AIOrb />
      <FocusOverlay />
      <Spotlight />
      <AICouncil />
      <MissionControl />
      <Settings />
    </div>
  )
}
