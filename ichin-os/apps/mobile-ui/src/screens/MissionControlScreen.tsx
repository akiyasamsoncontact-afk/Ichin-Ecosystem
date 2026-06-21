import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

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
]

export default function MissionControlScreen({ navigation }: any) {
  const insets = useSafeAreaInsets()

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backBtn}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Mission Control</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
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
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A0A',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backBtn: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.5)',
  },
  title: {
    fontSize: 18,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.8)',
  },
  content: {
    padding: 16,
    paddingBottom: 40,
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
