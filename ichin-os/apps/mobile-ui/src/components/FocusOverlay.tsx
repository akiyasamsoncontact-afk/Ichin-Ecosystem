import { View, Text, StyleSheet } from 'react-native'
import { useFocusStore } from '../stores/focusStore'

const FOCUS_CONFIG: Record<string, { label: string; description: string; color: string }> = {
  normal: { label: 'Normal Mode', description: 'All processes allowed', color: '#666' },
  focus: { label: 'Focus Mode', description: 'Distractions minimized', color: '#00E676' },
  deep_focus: { label: 'Deep Focus', description: 'Social/entertainment blocked', color: '#FFB300' },
  lock: { label: 'Lock Mode', description: 'Maximum restriction', color: '#FF5252' },
}

export default function FocusOverlay() {
  const mode = useFocusStore((s) => s.mode)
  const blockedProcesses = useFocusStore((s) => s.blockedProcesses)
  const config = FOCUS_CONFIG[mode]

  if (mode === 'normal') return null

  return (
    <View style={[styles.container, { backgroundColor: config.color + '10', borderColor: config.color + '30' }]}>
      <Text style={[styles.label, { color: config.color }]}>{config.label}</Text>
      <Text style={styles.desc}>{config.description}</Text>
      {blockedProcesses.length > 0 && (
        <View style={styles.blockedRow}>
          {blockedProcesses.map((p) => (
            <View key={p} style={styles.blockedChip}>
              <Text style={styles.blockedText}>Blocked: {p}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    alignItems: 'center',
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
  },
  desc: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.4)',
    marginTop: 2,
  },
  blockedRow: {
    flexDirection: 'row',
    gap: 6,
    marginTop: 6,
  },
  blockedChip: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  blockedText: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.3)',
  },
})
