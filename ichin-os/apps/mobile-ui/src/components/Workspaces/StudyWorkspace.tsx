import { useState } from 'react'
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native'

const TOPICS = [
  { id: 't1', name: 'Quantum Mechanics', progress: 65, cards: 42 },
  { id: 't2', name: 'Linear Algebra', progress: 80, cards: 28 },
  { id: 't3', name: 'Data Structures', progress: 45, cards: 56 },
  { id: 't4', name: 'Machine Learning', progress: 30, cards: 71 },
]

export default function StudyWorkspace() {
  const [selectedTopic, setSelectedTopic] = useState(TOPICS[0])

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.sectionTitle}>Topics</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.topicsRow}>
        {TOPICS.map((t) => {
          const isActive = selectedTopic.id === t.id
          return (
            <TouchableOpacity
              key={t.id}
              onPress={() => setSelectedTopic(t)}
              style={[styles.topicCard, isActive && styles.topicCardActive]}
            >
              <Text style={[styles.topicName, isActive && { color: '#4A9EFF' }]}>{t.name}</Text>
              <View style={styles.progressBar}>
                <View style={[styles.progressFill, { width: `${t.progress}%` }]} />
              </View>
              <Text style={styles.topicStats}>{t.progress}% · {t.cards} cards</Text>
            </TouchableOpacity>
          )
        })}
      </ScrollView>

      <View style={styles.mainCard}>
        <Text style={styles.mainCardTitle}>{selectedTopic.name}</Text>
        <Text style={styles.mainCardDesc}>Flashcard generation, quizzes, and notes available.</Text>
        <TouchableOpacity style={styles.actionBtn}>
          <Text style={styles.actionBtnText}>Generate Flashcards</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: '#4A9EFF' }]}>{selectedTopic.cards}</Text>
          <Text style={styles.statLabel}>Flashcards</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: '#4A9EFF' }]}>{Math.floor(selectedTopic.cards * 0.3)}</Text>
          <Text style={styles.statLabel}>Quizzes</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statValue, { color: '#4A9EFF' }]}>{selectedTopic.progress}%</Text>
          <Text style={styles.statLabel}>Progress</Text>
        </View>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(74, 158, 255, 0.02)',
  },
  content: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 8,
  },
  topicsRow: {
    marginBottom: 16,
  },
  topicCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 12,
    marginRight: 8,
    minWidth: 140,
  },
  topicCardActive: {
    backgroundColor: 'rgba(74, 158, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(74, 158, 255, 0.3)',
  },
  topicName: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.7)',
    fontWeight: '500',
    marginBottom: 6,
  },
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 2,
    marginBottom: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4A9EFF',
    borderRadius: 2,
  },
  topicStats: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.3)',
  },
  mainCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  mainCardTitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.7)',
    marginBottom: 8,
  },
  mainCardDesc: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.4)',
    textAlign: 'center',
    marginBottom: 16,
  },
  actionBtn: {
    backgroundColor: 'rgba(74, 158, 255, 0.15)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
  },
  actionBtnText: {
    color: '#4A9EFF',
    fontSize: 13,
    fontWeight: '500',
  },
  statsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '600',
  },
  statLabel: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: 4,
  },
})
