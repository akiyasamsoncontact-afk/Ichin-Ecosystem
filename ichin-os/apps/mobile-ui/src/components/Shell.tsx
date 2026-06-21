import { View, Text, TouchableOpacity, StyleSheet, Dimensions } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { useFocusStore } from '../stores/focusStore'
import { WORKSPACE_TITLES, WORKSPACE_COLORS } from '../types'
import type { WorkspaceType } from '../types'

const { width } = Dimensions.get('window')

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

const ORDER: WorkspaceType[] = ['study', 'coding', 'learning', 'personal']

export default function Shell() {
  const insets = useSafeAreaInsets()
  const activeWorkspace = useWorkspaceStore((s) => s.active)
  const setActive = useWorkspaceStore((s) => s.setActive)
  const focusMode = useFocusStore((s) => s.mode)

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Text style={styles.title}>{WORKSPACE_TITLES[activeWorkspace]}</Text>
        <View style={[styles.focusBadge, { backgroundColor: FOCUS_COLORS[focusMode] + '20' }]}>
          <Text style={[styles.focusText, { color: FOCUS_COLORS[focusMode] }]}>
            {FOCUS_LABELS[focusMode]}
          </Text>
        </View>
      </View>
      <View style={styles.workspaceRow}>
        {ORDER.map((ws) => {
          const isActive = ws === activeWorkspace
          return (
            <TouchableOpacity
              key={ws}
              onPress={() => setActive(ws)}
              style={[
                styles.wsTab,
                isActive && { backgroundColor: WORKSPACE_COLORS[ws] + '20', borderColor: WORKSPACE_COLORS[ws], borderWidth: 1 },
              ]}
            >
              <Text style={[styles.wsTabText, { color: isActive ? WORKSPACE_COLORS[ws] : '#666' }]}>
                {ws.charAt(0).toUpperCase() + ws.slice(1)}
              </Text>
            </TouchableOpacity>
          )
        })}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#0A0A0A',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.8)',
  },
  focusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  focusText: {
    fontSize: 10,
    fontWeight: '500',
  },
  workspaceRow: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingBottom: 8,
    gap: 6,
  },
  wsTab: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  wsTabText: {
    fontSize: 12,
    fontWeight: '500',
  },
})
