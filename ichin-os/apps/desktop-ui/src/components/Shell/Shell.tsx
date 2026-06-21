import { Search, LayoutDashboard, Settings } from 'lucide-react'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import { useFocusStore } from '../../stores/focusStore'
import { useSpotlightStore } from '../../stores/spotlightStore'
import { useUIStore } from '../../stores/uiStore'

const WORKSPACE_LABELS: Record<string, string> = {
  study: 'Study Space',
  coding: 'Coding Space',
  learning: 'Learning Path',
  personal: 'Personal Space',
}

const FOCUS_LABELS: Record<string, string> = {
  normal: 'Normal',
  focus: 'Focus',
  deep_focus: 'Deep Focus',
  lock: 'Lock',
}

const FOCUS_COLORS: Record<string, string> = {
  normal: '#666',
  focus: '#00E676',
  deep_focus: '#FFB300',
  lock: '#FF5252',
}

export default function Shell() {
  const activeWorkspace = useWorkspaceStore((s) => s.active)
  const focusMode = useFocusStore((s) => s.mode)
  const openSpotlight = useSpotlightStore((s) => s.open)
  const toggleMissionControl = useUIStore((s) => s.setMissionControlOpen)
  const toggleSettings = useUIStore((s) => s.setSettingsOpen)

  return (
    <div className="flex items-center justify-between h-12 px-4 glass" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-white/80">
          {WORKSPACE_LABELS[activeWorkspace] || 'Workspace'}
        </span>
        <span
          className="text-xs px-2 py-0.5 rounded-full"
          style={{
            backgroundColor: FOCUS_COLORS[focusMode] + '20',
            color: FOCUS_COLORS[focusMode],
          }}
        >
          {FOCUS_LABELS[focusMode]}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={openSpotlight}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs text-white/40 hover:text-white/60 hover:bg-white/5 transition-all"
        >
          <Search size={14} />
          <span>Search...</span>
          <kbd className="text-[10px] px-1 py-0.5 rounded bg-white/5 text-white/30">^Space</kbd>
        </button>
        <button
          onClick={() => toggleMissionControl(true)}
          className="p-2 rounded-lg text-white/40 hover:text-white/60 hover:bg-white/5 transition-all"
          title="Mission Control"
        >
          <LayoutDashboard size={16} />
        </button>
        <button
          onClick={() => toggleSettings(true)}
          className="p-2 rounded-lg text-white/40 hover:text-white/60 hover:bg-white/5 transition-all"
          title="Settings"
        >
          <Settings size={16} />
        </button>
      </div>
    </div>
  )
}
