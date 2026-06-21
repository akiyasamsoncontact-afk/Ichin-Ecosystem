import { useEffect } from 'react'
import Sidebar from './Sidebar'
import Shell from './Shell'
import Container from '../Workspace/Container'
import AIOrb from '../Orb/AIOrb'
import Spotlight from '../Spotlight/Spotlight'
import AICouncil from '../Council/AICouncil'
import FocusOverlay from '../Focus/FocusOverlay'
import MissionControl from '../MissionControl/MissionControl'
import Settings from '../Settings/Settings'
import KeyboardCheatsheet from '../Cheatsheet/KeyboardCheatsheet'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import { useFocusStore } from '../../stores/focusStore'
import { useSpotlightStore } from '../../stores/spotlightStore'
import { useCouncilStore } from '../../stores/councilStore'
import { useUIStore } from '../../stores/uiStore'
import { useAppStore } from '../../stores/appStore'

export default function AppShell() {
  const cycleWorkspace = useWorkspaceStore((s) => s.cycle)
  const cycleFocus = useFocusStore((s) => s.cycleMode)
  const loadFocusState = useFocusStore((s) => s.loadFocusState)
  const openSpotlight = useSpotlightStore((s) => s.open)
  const openCouncil = useCouncilStore((s) => s.open)
  const {
    setMissionControlOpen,
    setSettingsOpen,
    setCheatsheetOpen,
  } = useUIStore()
  const loadMemories = useAppStore((s) => s.loadMemories)
  const loadTasks = useAppStore((s) => s.loadTasks)

  useEffect(() => {
    loadFocusState()
    loadMemories()
    loadTasks()
  }, [])

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const ctrl = e.ctrlKey || e.metaKey
      if (!ctrl) return

      switch (e.code) {
        case 'Space':
          e.preventDefault()
          openSpotlight()
          break
        case 'KeyA':
          e.preventDefault()
          openCouncil()
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
    <div className="h-full w-full flex flex-col bg-bg text-text">
      <Shell />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Container />
        </main>
      </div>
      <AIOrb />
      <Spotlight />
      <AICouncil />
      <FocusOverlay />
      <MissionControl />
      <Settings />
      <KeyboardCheatsheet />
    </div>
  )
}
