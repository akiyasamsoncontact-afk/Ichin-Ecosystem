import { useState } from 'react'
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Image } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import Shell from '../components/Shell'
import Spotlight from '../components/Spotlight'
import AICouncil from '../components/AICouncil'
import AIOrb from '../components/AIOrb'
import FocusOverlay from '../components/FocusOverlay'
import { useOrbStore } from '../stores/orbStore'

const QUICK_ACTIONS = [
  { label: 'Ask AI', icon: '◉' },
  { label: 'Search', icon: '⌕' },
  { label: 'Tasks', icon: '☰' },
  { label: 'Focus', icon: '◎' },
]

const RECENT_ACTIVITY = [
  { text: 'Study: Quantum Mechanics flashcards reviewed', time: '10m ago' },
  { text: 'AI Council resolved code review request', time: '25m ago' },
  { text: 'Focus mode ended — 1h 45m session', time: '2h ago' },
]

export default function HomeScreen() {
  const insets = useSafeAreaInsets()
  const orbState = useOrbStore((s) => s.state)
  const [spotlightVisible, setSpotlightVisible] = useState(false)
  const [councilVisible, setCouncilVisible] = useState(false)

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <FocusOverlay />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.greeting}>Good morning.</Text>
        <Text style={styles.subtitle}>What would you like to do today?</Text>

        <TouchableOpacity
          onPress={() => setSpotlightVisible(true)}
          style={styles.searchBar}
        >
          <Text style={styles.searchIcon}>⌕</Text>
          <Text style={styles.searchPlaceholder}>Search commands, files, or ask AI...</Text>
        </TouchableOpacity>

        <View style={styles.quickActions}>
          <TouchableOpacity style={styles.quickAction} onPress={() => setCouncilVisible(true)}>
            <Text style={styles.quickActionIcon}>◉</Text>
            <Text style={styles.quickActionLabel}>Ask AI</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickAction} onPress={() => setSpotlightVisible(true)}>
            <Text style={styles.quickActionIcon}>⌕</Text>
            <Text style={styles.quickActionLabel}>Search</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickAction}>
            <Text style={styles.quickActionIcon}>☰</Text>
            <Text style={styles.quickActionLabel}>Tasks</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickAction}>
            <Text style={styles.quickActionIcon}>◎</Text>
            <Text style={styles.quickActionLabel}>Focus</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.orbStatus}>
          <View style={[styles.orbStatusDot, {
            backgroundColor: orbState === 'active' ? '#00E676' : orbState === 'critical' ? '#FF5252' : '#4A9EFF'
          }]} />
          <Text style={styles.orbStatusText}>
            AI Orb is {orbState}
          </Text>
        </View>

        <Text style={styles.sectionTitle}>Recent Activity</Text>
        {RECENT_ACTIVITY.map((a, i) => (
          <View key={i} style={styles.activityItem}>
            <Text style={styles.activityText}>{a.text}</Text>
            <Text style={styles.activityTime}>{a.time}</Text>
          </View>
        ))}

        <View style={styles.workspacePreview}>
          <Text style={styles.previewTitle}>Quick Access</Text>
          <View style={styles.previewGrid}>
            <TouchableOpacity style={styles.previewCard}>
              <Text style={styles.previewIcon}>📚</Text>
              <Text style={styles.previewLabel}>Study</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.previewCard}>
              <Text style={styles.previewIcon}>💻</Text>
              <Text style={styles.previewLabel}>Coding</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.previewCard}>
              <Text style={styles.previewIcon}>🧠</Text>
              <Text style={styles.previewLabel}>Learning</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.previewCard}>
              <Text style={styles.previewIcon}>👤</Text>
              <Text style={styles.previewLabel}>Personal</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      <AIOrb />
      <Spotlight visible={spotlightVisible} onClose={() => setSpotlightVisible(false)} />
      <AICouncil visible={councilVisible} onClose={() => setCouncilVisible(false)} />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A0A',
  },
  content: {
    padding: 20,
    paddingBottom: 100,
  },
  greeting: {
    fontSize: 24,
    fontWeight: '300',
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.4)',
    marginBottom: 20,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    marginBottom: 24,
  },
  searchIcon: {
    fontSize: 18,
    color: 'rgba(255,255,255,0.2)',
    marginRight: 10,
  },
  searchPlaceholder: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.2)',
  },
  quickActions: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 24,
  },
  quickAction: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
  },
  quickActionIcon: {
    fontSize: 20,
    color: 'rgba(255,255,255,0.4)',
    marginBottom: 6,
  },
  quickActionLabel: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.5)',
  },
  orbStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginBottom: 24,
  },
  orbStatusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  orbStatusText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    textTransform: 'capitalize',
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
  },
  activityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.03)',
  },
  activityText: {
    flex: 1,
    fontSize: 12,
    color: 'rgba(255,255,255,0.5)',
  },
  activityTime: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.2)',
    marginLeft: 8,
  },
  workspacePreview: {
    marginTop: 20,
  },
  previewTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
  },
  previewGrid: {
    flexDirection: 'row',
    gap: 8,
  },
  previewCard: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
  },
  previewIcon: {
    fontSize: 22,
    marginBottom: 6,
  },
  previewLabel: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.5)',
  },
})
