import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Modal } from 'react-native'

const STATS = [
  { label: 'System Health', value: '98%', color: '#00E676' },
  { label: 'Focus Time', value: '4h 32m', color: '#4A9EFF' },
  { label: 'Tasks Done', value: '12/18', color: '#B388FF' },
  { label: 'AI Decisions', value: '147', color: '#FFB300' },
]

const RECENT_ACTIONS = [
  { time: '2m ago', text: 'AI Council resolved query about project structure' },
  { time: '15m ago', text: 'Focus Mode activated for coding session' },
  { time: '32m ago', text: 'Memory consolidation completed (142 items)' },
  { time: '1h ago', text: 'New workflow created: Daily Standup Report' },
  { time: '2h ago', text: 'App installed: Advanced Markdown Editor' },
]

interface Props {
  visible: boolean
  onClose: () => void
}

export default function MissionControl({ visible, onClose }: Props) {
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <TouchableOpacity activeOpacity={1} onPress={onClose} style={styles.backdrop}>
        <ScrollView style={styles.container} contentContainerStyle={styles.content}>
          <View style={styles.header}>
            <Text style={styles.title}>Mission Control</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.closeBtn}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.statsGrid}>
            {STATS.map((stat) => (
              <View key={stat.label} style={styles.statCard}>
                <Text style={styles.statLabel}>{stat.label}</Text>
                <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
              </View>
            ))}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Actions</Text>
            {RECENT_ACTIONS.map((a, i) => (
              <View key={i} style={styles.actionRow}>
                <Text style={styles.actionTime}>{a.time}</Text>
                <View style={styles.actionDot} />
                <Text style={styles.actionText}>{a.text}</Text>
              </View>
            ))}
          </View>
        </ScrollView>
      </TouchableOpacity>
    </Modal>
  )
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
  },
  container: {
    flex: 1,
    paddingTop: 60,
    paddingHorizontal: 16,
  },
  content: {
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: '300',
    color: 'rgba(255,255,255,0.8)',
  },
  closeBtn: {
    fontSize: 18,
    color: 'rgba(255,255,255,0.3)',
    padding: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 16,
  },
  statLabel: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.4)',
    marginBottom: 6,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '300',
  },
  section: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 12,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  actionTime: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.2)',
    width: 50,
  },
  actionDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginHorizontal: 8,
  },
  actionText: {
    flex: 1,
    fontSize: 12,
    color: 'rgba(255,255,255,0.5)',
  },
})
